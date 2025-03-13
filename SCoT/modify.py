import os
import subprocess
import re

def run_command(command):
    """Execute a shell command and return the result."""
    return subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def run_pylint(file_path):
    """Run pylint on a file and return all Errors (E codes) that can prevent execution."""
    if os.path.exists(file_path):
        result = subprocess.run(
            ["pylint",
             "--disable=all",           # Turn off all checks
             "--enable=E",  # Enable all Errors (E), Fatal errors, and Syntax errors
             "--reports=no",            # Disable summary reports
             "--persistent=no",         # Don't remember previous runs
             file_path],
            capture_output=True,
            text=True
        )
        return result.stdout.strip() + "\n" + result.stderr.strip()
    else:
        return f"File {file_path} does not exist.\n"

def get_error_lines(pylint_output):
    """
    Extract error lines from pylint output, only taking lines with error codes starting with 'E'.
    For example, the error line
      example.py:2:11: E0602: Undefined variable 'abc' (undefined-variable)
    will be extracted as is.
    """
    error_lines = set()
    pattern = r"^.*?:\d+:\d+:\s+E\d+:.*\(.+\)$"
    for line in pylint_output.splitlines():
        line = line.strip()
        if re.match(pattern, line):
            error_lines.add(line)
    return error_lines

def format_error_set(errors):
    """Format a set of errors into a string for display."""
    result = ""
    for error in sorted(errors):
        result += " - " + error + "\n"
    return result

def replace_code(bot_code, file_path, start, end):
    """
    Replace code in a file from line 'start' to 'end' (inclusive).
    If start == end: replace that specific line.
    If start < end: replace the entire block from line 'start' to line 'end'.
    """
    try:
        if start > end:
            raise ValueError("Start line must be less than or equal to end line.")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = bot_code.splitlines(keepends=True)
        # Ensure the last line has a newline character
        if new_lines and not new_lines[-1].endswith('\n'):
            new_lines[-1] += "\n"
        insert_index = start - 1

        # If replacing a single line (start == end), replace that line
        if start == end:
            lines = lines[:insert_index] + new_lines + lines[insert_index:]
        else:
            # If start < end, replace from line 'start' to line 'end'
            lines[insert_index:end-1] = new_lines

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

    except Exception as e:
        print("An error occurred during replacement: " + str(e))

def view_code(file_path: str, start_line: int, end_line: int) -> None:
    result = '## Code after being updated\n'
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        code_snippet = ''.join(lines[start_line-1:end_line])
        if code_snippet.endswith('\n'): code_snippet = code_snippet[:-1]
        
        result += f"Lines: {start_line}-{end_line} (The first line in the code is line {start_line}, the last line is line {end_line})\n"
        result += f"```python\n{code_snippet}\n```\n"
        return result
        
    except Exception as e:
        return f"Error reading file: {str(e)}"

def validate_replacement_code(bot_code, file_path, start, end):
    print(f"Perform replacing code at file {file_path} from line {start} to {end}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except Exception as e:
        return "Unable to read file: " + str(e).replace('---', '').replace('***','')

    pylint_before = run_pylint(file_path)
    error_lines_before = get_error_lines(pylint_before)

    replace_code(bot_code, file_path, start, end)
    new_end = start + len(bot_code.split('\n'))
    new_code = view_code(file_path, max(start - 5, 1), new_end + 5)

    pylint_after = run_pylint(file_path)
    error_lines_after = get_error_lines(pylint_after)

    if not error_lines_after.issubset(error_lines_before):
        new_errors = error_lines_after - error_lines_before
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        return f"Replacement results in the new code:\n {new_code}\nNew errors have appeared:\n{format_error_set(new_errors)}Roll back to the original code." \
                .replace('---', '').replace('***','')
    else:
        return f"Replacement results in the new code:\n {new_code}\nNo new errors introduced after replacement.\nDetails:\n{pylint_after}" \
            .replace('---', '').replace('***','')

