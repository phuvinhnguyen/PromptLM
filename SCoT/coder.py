from SCoT.envchat import *
from SCoT.utils import *
import SCoT

utils_path = os.path.join(os.path.dirname(SCoT.__file__), 'patch.py')
with open(utils_path, 'r') as file:
    PATCH_CODE = file.read()

apply_code = '''
print(validate_patch(\'\'\'{diff_text}\'\'\', \'./\').replace(\'***\', \'\').replace(\'---\', \'\'))
'''

env_response = '''# Environment
Run a script to apply patch to {root}, then check for possible error using Pylint
## Notification of the patch status
{stdout}'''

code_system_prompt = '''# Task
You are a coder that will solve the existing problem of the project by creating exactly one patch text for each of your answers. Your patch will be applied automatically by the environment, if there are any errors during the patch process, the environment will inform you of the error for you to re-generate another patch. The tasker will give you information about the problem and where to edit it to fix it. If the Tasker does not give you the edit place and you have no information to generate the patch, your patch text section must be \'pass\'. Your answers must strictly follow the output format.
# Output Format
## Think
your step-by-step and careful thinking on how to patch the code to solve the problem
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

```
If multiple patch texts are provided, only the last one is considered.
'''

code_initial_task = '''# Tasker
## Problem to solve
{problem}
This is the location of code pieces and contents that should be modified to solve the problem:
{answer}
Your patch will be applied at path {root}, carefully consider this information when generating file path in your patch text'''

class CoderEnv(Environment):
    def get_code(self, markdown_text):
        text: str = extract_code(markdown_text)[-1]
        if text[-1] != '\n': text += '\n'
        return 'python', PATCH_CODE + apply_code.format(diff_text=text)

class Coder(EnvChat):
    system_prompt = code_system_prompt
    env_prompt = env_response
    initial_task = code_initial_task
    modifies = ()

    def __init__(self, chatbot, max_time=12, max_history=14):
        super().__init__(chatbot, max_time, max_history)
        self.env = CoderEnv(self.env_prompt, self.code_wrap)
    
    def exec(self, root, problems):
        patch = extract_sections(self.history[-1].content)[-1]
        if patch.lower().strip() == 'pass': return  ()
        answer = self.env.run(patch, root)
        if 'Valid patch, Pylint does not detect new error after applying this patch:' in answer:
            return ()
        return answer
