from SCoT.envchat import *
from SCoT.utils import *

apply_code = '''
import os
import subprocess
import tempfile
import re

def run_command(command):
    return subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def create_patch_file(patch_text):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False) as tmp:
        tmp.write(patch_text)
        return tmp.name

def extract_changed_files(patch_text):
    changed_files = set()
    for line in patch_text.splitlines():
        if line.startswith("diff --git"):
            parts = line.split()
            if len(parts) >= 3:
                a_file = parts[2]  # dạng "a/example.py"
                if a_file.startswith("a/"):
                    changed_files.add(a_file[2:])
                else:
                    changed_files.add(a_file)
    return list(changed_files)

def get_current_commit():
    result = run_command(["git", "rev-parse", "HEAD"])
    if result.returncode != 0:
        raise Exception("Error when retrieving current commit: " + result.stderr.strip())
    return result.stdout.strip()

def check_patch(patch_file):
    result = run_command(["git", "apply", "--check", patch_file])
    if result.returncode != 0:
        raise Exception("Invalid patch: \\n" + result.stderr.strip())

def apply_patch(patch_file):
    result = run_command(["git", "apply", patch_file])
    if result.returncode != 0:
        raise Exception("Patch cannot be applied: " + result.stderr.strip())

def run_pylint_on_files(changed_files):
    output = ""
    for file in changed_files:
        if os.path.exists(file):
            result = run_command(["pylint", file])
            output += f"Output of {{file}}:\\n{{result.stdout}}\\n{{result.stderr}}\\n"
        else:
            output += f"File {{file}} does not exist after applying the patch.\\n"
    return output

def rollback(commit_hash):
    run_command(["git", "reset", "--hard", commit_hash])

def get_error_lines(pylint_output):
    error_lines = set()
    pattern = r"^.*?:\\d+:\\d+:\\s+E\\d+:.*\\(.+\\)$"
    for line in pylint_output.splitlines():
        line = line.strip()
        if re.match(pattern, line):
            error_lines.add(line)
    return error_lines

def format_error_set(errors):
    result = ""
    for error in sorted(errors):
        result += " - " + error + "\\n"
    return result

def validate_patch(patch_text, project_root):
    old_cwd = os.getcwd()
    patch_file = None
    try:
        os.chdir(project_root)
        patch_file = create_patch_file(patch_text)
        
        check_patch(patch_file)
        
        current_commit = get_current_commit()
        
        changed_files = extract_changed_files(patch_text)
        if not changed_files:
            return "Cannot find any change files in the patch"
        
        pylint_before = run_pylint_on_files(changed_files)
        error_lines_before = get_error_lines(pylint_before)
        
        apply_patch(patch_file)
        
        pylint_after = run_pylint_on_files(changed_files)
        error_lines_after = get_error_lines(pylint_after)
        
        if not error_lines_after.issubset(error_lines_before):
            new_errors = error_lines_after - error_lines_before
            rollback(current_commit)
            return ("Invalid patch, Pylint detect new error after applying the patch:\\n{{}}"
                    .format(format_error_set(new_errors)))
        else:
            return ("Valid patch, Pylint does not detect new error after applying this patch:\\n{{}}"
                    .format(pylint_after))
    except Exception as e:
        return "Patch cannot be applied\\n" + str(e)
    finally:
        if patch_file and os.path.exists(patch_file):
            os.remove(patch_file)
        os.chdir(old_cwd)

print(validate_patch(\'\'\'{diff_text}\'\'\', \'./\').replace(\'***\', \'\').replace(\'---\', \'\'))
'''

env_response = '''# Environment
Run a script to apply patch to {root}, then check for possible error using Pylint
## Notification of the patch status
{stdout}'''

code_system_prompt = '''# Task
You are coder that will solve the existing problem of the project by creating exactly one patch text for each of your answer. Your patch will be applied automatically by the environment, if there are any errors during the patch process, the environment will inform you the error for you to re-generate another patch. Tasker will give you the information of the problem and where to edit to fix it. If the Tasker does not give you the edit place and you completely have no information to generate the patch, your patch text section must be \'pass\'. Your answers must strictly follow the output format.
# Output Format
## Think
your step by step and careful thinking on how to patch the code to solve the problem
## Patch text
Your patch text in a code block, for example:
```diff
diff --git a/src/main.py b/src/main.py
index 495a0f3..65d6ed5 100644
--- a/src/main.py
+++ b/src/main.py
@@ -2,4 +2,4 @@ print("Hello World"
 
 def calculate():
     result = 5 * 3
-    return reslt
+    return result
```'''

code_initial_task = '''# Tasker
## Problem to solve
{problem}
This is the location of code pieces and contents that should be modified to solve the problem:
{answer}
Your patch will be applied at path {root}, carefully consider this information when generating file path in your patch text'''

class CoderEnv(Environment):
    def get_code(self, markdown_text):
        _, text = extract_code(markdown_text)
        return 'python', apply_code.format(diff_text=text)

class Coder(EnvChat):
    system_prompt = code_system_prompt
    env_prompt = env_response
    initial_task = code_initial_task
    modifies = ()

    def __init__(self, chatbot, max_time=10, max_history=10):
        super().__init__(chatbot, max_time, max_history)
        self.env = CoderEnv(self.env_prompt, self.code_wrap)
    
    def exec(self, root, problems):
        patch = extract_sections(self.history[-1].content)[-1]
        if patch.lower().strip() == 'pass': return  ()
        answer = self.env.run(patch, root)
        if 'Valid patch, Pylint does not detect new error after applying this patch:' in answer:
            return ()
        return answer
