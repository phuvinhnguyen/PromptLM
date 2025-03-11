import tempfile
from typing import Set, List
import os, subprocess, re

def run_command(command: List[str]) -> subprocess.CompletedProcess:
    """Execute a shell command and return the result."""
    return subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False
    )

def create_patch_file(patch_text: str) -> str:
    """Create a temporary patch file with the given content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False) as tmp:
        tmp.write(patch_text)
        return tmp.name

def extract_changed_files(patch_text: str) -> List[str]:
    """Extract list of changed files from patch content with improved parsing."""
    changed_files = set()
    current_file = None
    
    for line in patch_text.split('\n'):
        # Handle diff headers
        if line.startswith('diff --git'):
            parts = line.split()
            if len(parts) >= 3:
                current_file = parts[2][2:]  # Strip 'a/' prefix
                changed_files.add(current_file)
        
        # Handle new and deleted files
        elif line.startswith('--- ') or line.startswith('+++ '):
            file_path = line[4:].split('\t')[0].strip()
            if file_path != '/dev/null':
                changed_file = file_path[2:] if file_path.startswith('a/') else file_path
                changed_files.add(changed_file)
        
        # Handle renames
        elif line.startswith('rename from '):
            changed_files.add(line[len('rename from '):])
        elif line.startswith('rename to '):
            changed_files.add(line[len('rename to '):])

    return sorted([f for f in changed_files if f])

def get_current_commit() -> str:
    """Get the current HEAD commit hash."""
    result = run_command(["git", "rev-parse", "HEAD"])
    if result.returncode != 0:
        raise RuntimeError(f"Failed to get current commit: {result.stderr.strip()}")
    return result.stdout.strip()

def check_patch(patch_file: str) -> None:
    """Check if patch can be applied."""
    result = run_command(["git", "apply", "--check", patch_file])
    if result.returncode != 0:
        raise RuntimeError(f"Patch check failed: {result.stderr.strip()}")

def apply_patch(patch_file: str) -> None:
    """Apply the patch to the repository."""
    result = run_command(["git", "apply", "--whitespace=fix", patch_file])
    if result.returncode != 0:
        raise RuntimeError(f"Patch application failed: {result.stderr.strip()}")

def run_pylint_on_files(files: List[str]) -> str:
    """Run pylint to detect only syntax errors in specified files."""
    valid_files = [f for f in files if os.path.exists(f)]
    
    if not valid_files:
        return "No existing files to lint"
    
    # Configure pylint to only check for syntax errors
    pylint_cmd = [
        "pylint",
        "--disable=all",          # Turn off all checks
        "--enable=syntax-error",  # Enable only syntax checks
        "--reports=no",           # Disable summary reports
        "--persistent=no",        # Don't remember previous runs
        *valid_files
    ]
    
    result = run_command(pylint_cmd)
    
    # Filter only syntax error messages (E0001)
    syntax_errors = []
    error_pattern = r"^([^:]+):(\d+):\d+:\s+(E0001):\s+(.*)"
    
    for line in result.stdout.split('\n'):
        match = re.match(error_pattern, line)
        if match:
            filename, line_num, err_code, message = match.groups()
            syntax_errors.append(f"{filename}:{line_num} - {message}")
    
    return "\n".join(syntax_errors) if syntax_errors else "No syntax errors found"

def get_error_lines(pylint_output: str) -> Set[str]:
    """Extract unique error lines from pylint output with better regex."""
    errors = set()
    pattern = r"^([^:]+):(\d+):\d+: (\w+): (.*) \(.*\)$"
    
    for line in pylint_output.split('\n'):
        match = re.match(pattern, line)
        if match:
            filename, line_num, err_type, message = match.groups()
            errors.add(f"{filename}:{line_num}: {err_type}: {message}")
    
    return errors

def format_errors(errors: Set[str]) -> str:
    """Format errors for human-readable output."""
    if not errors:
        return "No errors found"
    return "\n".join(sorted(errors))

def validate_patch(patch_text: str, project_root: str) -> str:
    """Validate a patch with improved error handling and rollback."""
    # if patch_text[-1] != '\n': patch_text = patch_text + '\n'
    original_dir = os.getcwd()
    patch_file = None
    
    try:
        os.chdir(project_root)
        patch_file = create_patch_file(patch_text)
        
        # Initial checks
        check_patch(patch_file)
        original_commit = get_current_commit()
        changed_files = extract_changed_files(patch_text)
        
        if not changed_files:
            return "Error: No changed files detected in patch"
        
        # Capture pre-patch state
        pre_errors = get_error_lines(run_pylint_on_files(changed_files))
        
        # Apply patch and capture post-patch state
        apply_patch(patch_file)
        post_errors = get_error_lines(run_pylint_on_files(changed_files))
        
        # Analyze differences
        new_errors = post_errors - pre_errors
        fixed_errors = pre_errors - post_errors
        
        if new_errors:
            run_command(["git", "reset", "--hard", original_commit])
            run_command(["git", "clean", "-fd"])
            return (
                "Patch introduced new errors:\n"
                f"{format_errors(new_errors)}\n\n"
                "Changes rolled back successfully."
            )
        
        return (
            "Patch applied successfully. "
            f"Fixed errors: {len(fixed_errors)}\n"
            f"Remaining errors: {len(post_errors)}"
        )
    
    except Exception as e:
        # Cleanup on failure
        if 'original_commit' in locals():
            run_command(["git", "reset", "--hard", original_commit])
            run_command(["git", "clean", "-fd"])
        return f"Validation failed: {str(e)}"
    
    finally:
        if patch_file and os.path.exists(patch_file):
            os.remove(patch_file)
        os.chdir(original_dir)