import re
from SCoT.tools import *
import inspect
import subprocess
import tempfile
from typing import Set, List

def extract_sections(text):
    sections = re.findall(r'(?s)##\s+(.*?)\n(.*?)(?=\n##\s+|\Z)', text)
    output = [content.strip() for _, content in sections]
    return tuple(output)

def extract_code(text):
    matches = re.findall(r'```(\w+)?\n(.*?)\n```', text, re.DOTALL)
    if matches: return matches[-1]
    return None, None

def get_tools_description(tools = [summary_dir, search_module, search_name, listdir, view_code]):
    description = ''
    for tool in tools:
        signature = inspect.signature(tool)
        header = f"- def {tool.__name__}{signature}"
        description += f'{header}\nDocument: {tool.__doc__}\n\n'
    return description

def get_tools_code():
    tools_path = os.path.join(os.path.dirname(__file__), "tools.py")
    with open(tools_path, "r", encoding="utf-8") as f:
        tools_code = f.read()
    return tools_code + '\n\n'

def extract_modified_files(patch_text):
    """Extract modified file paths from a patch text."""
    files = set()
    for line in patch_text.splitlines():
        match = re.match(r'^\+\+\+ b/(.+\.py)', line)  # Find modified Python files
        if match:
            files.add(match.group(1))
    for file in list(files):
        subprocess.run(["pylint", "--errors-only", file])


def check_syntax(patch_text, root_dir):
    files = set()
    for line in patch_text.split('\n'):
        if line.startswith('+++ '):
            file_part = line[4:].strip()
            if file_part.startswith('b/'):
                file_part = file_part[2:]
            if file_part == '/dev/null' or os.path.isabs(file_part):
                continue
            files.add(file_part)
    
    result = []
    for file_path in files:
        full_path = os.path.join(root_dir, file_path)
        if not os.path.isfile(full_path) or not file_path.endswith('.py'):
            continue        
        cmd = [
            'pylint',
            '--disable=all',
            '--enable=F',
            '--exit-zero',
            '--output-format=text',
            file_path
        ]
        try:
            proc = subprocess.run(
                cmd,
                cwd=root_dir,
                capture_output=True,
                text=True,
                check=False
            )
        except Exception:
            continue
        
        output = proc.stdout
        errors = []
        for line in output.split('\n'):
            if line.startswith(f"{file_path}:"):
                parts = line.split(':', 3)
                if len(parts) >= 4:
                    error_msg = parts[3].strip()
                    errors.append(error_msg)
        
        if errors:
            result.append(file_path)
            result.append("Error:")
            result.extend(errors)
    
    return '\n'.join(result)

def search_name_similar(directory, sname, max_results=15):
    matches = []
    
    for root, dirs, files in os.walk(directory):
        for name in dirs + files:
            if sname.lower() in name.lower():
                matches.append(os.path.join(root, name))
                if len(matches) > max_results: break
        if len(matches) > max_results:
            break

    output = f"\nSearch Results: Folders and files containing '{sname}'\n"
    
    if not matches:
        output += "No matching files or folders found."
    else:
        output += "\n".join(f"  {path}" if os.path.isdir(path) else f"  {path}" for path in matches[:max_results])

        if len(matches) > max_results:
            output += f"\n\nShowing only the first {max_results} results. More matches exist!"

    return output

## Patching

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
    if patch_text[-1] != '\n': patch_text = patch_text + '\n'
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