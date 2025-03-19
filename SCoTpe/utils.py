import re
from SCoT.tools import *
import inspect
import subprocess
from .patch import *

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