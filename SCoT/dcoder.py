from SCoT.envchat import *
from SCoT.utils import *
import SCoT
import json

utils_path = os.path.join(os.path.dirname(SCoT.__file__), 'modify.py')
with open(utils_path, 'r') as file:
    PATCH_CODE = file.read()

apply_code = '''
print(validate_replacement_code(\'\'\'{code}\'\'\', \'{path}\', {start}, {end}))
'''

env_response = '''# Environment
Run a script to apply change to {root}, then check for possible error using Pylint
## Notification of the patch status
{stdout}'''

code_system_prompt = '''# Task
You are a coder responsible for fixing an existing issue in a project by modifying specific sections of a file. Your task is to generate a Python dictionary that specifies:  

- The file path of the file that needs editing.  
- The start line and end line that define the section to be modified.  
- The Python code that will replace the specified section to resolve the issue.  

## **Replacement Rules:**  
- If `start_line < end_line`, the lines from `start_line` to `end_line - 1` will be replaced with your new Python code.  
- If `start_line == end_line`, no existing lines will be removed, and your new code will be inserted at `start_line`.  
- The modification will be applied if there are no new syntax errors introduced.

Your response must strictly follow this structure, which includes step-by-step thinking and valid json objects (Python dictionary) as the final conclusion.

# **Output Format:**  

## Think
- Analyze the problem thoroughly before making modifications.  
- Ensure that your patch effectively fixes the issue.  
- Keep the new code concise, efficient, and aligned with best practices.  
- If the Tasker does not give you the edit place and you have no information to generate the code, your conclusion must be \'pass\'
## Conclusion
```json
{
  "file": "<path_to_file>",
  "start_line": <integer>,
  "end_line": <integer>,
  "python_code": "<modified Python code>"
}
```'''

code_initial_task = '''# Tasker
## Problem to solve
{problem}
This is the location of code pieces and contents that should be modified to solve the problem:
{answer}
Your patch will be applied at path {root}, carefully consider this information when generating file path in your patch text'''

import re
import json

def extract_json(text):
    # Find all potential JSON objects in the text
    matches = re.findall(r'\{.*?\}', text, re.DOTALL)

    json_objects = []
    for match in matches:
        try:
            json_obj = json.loads(match)  # Parse each matched JSON string
            json_objects.append(json_obj)
        except json.JSONDecodeError:
            print(f"Warning: Skipping invalid JSON: {match}")

    return json_objects

class CoderEnv(Environment):
    def get_code(self, data):
        code = '\n'.join([apply_code.format(
            code=i['python_code'],
            path=i['file'],
            start=i['start_line'],
            end=i['end_line']) for i in data])

        return 'python', PATCH_CODE + code

class DirectCoder(EnvChat):
    system_prompt = code_system_prompt
    env_prompt = env_response
    initial_task = code_initial_task
    modifies = ()

    def __init__(self, chatbot, max_time=10, max_history=12):
        super().__init__(chatbot, max_time, max_history)
        self.env = CoderEnv(self.env_prompt, self.code_wrap)
    
    def exec(self, root, problems):
        conclusion = extract_sections(self.history[-1].content)[-1]
        if conclusion.lower().strip() == 'pass': return ()

        data = extract_json(conclusion)
        answer = self.env.run(data, root)

        if 'Replacement valid. No new errors introduced after replacement.' in answer:
            return ()
        return answer
