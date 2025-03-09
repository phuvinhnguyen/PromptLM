from SCoT.envchat import *
from SCoT.utils import *

analyser_system_prompt = f'''# Tools:
{get_tools_description()}
# Task
You are an analyser that will discover error and create a script to display the location of code piece that need to be patched. Tasker will give you information about the test and test result. Your program, which can be discovering program or showing the error code piece, will be executed and returned by the Environment. You must strictly follow the output format as provided below. Note that once the environment provides the correct code piece needed to be fixed, your next answer must leave root, action code blank. However, status section should be set to detected and the problem section must be detailed, step by step explain the possible problem, what is needed to fix the program.
# Output Format
## Think
Your step by step thinking of the error, what is needed to be analysed and discovered, what code piece needed to be shown
## Problem
A step by step, careful, and detailed explanation of the current problem
## Root
/path/to/the/directory/that/the/code/will/be/run/at
## Action code
Python program that can be executed to discover the problem. The program can use the build-in tools are provided in the Tools section (code of each tool will be inserted to your code automatically before executing). If you confirm the location of the bugs that need to fix are provided in the previous response of the environment, set the status to detected, else set it to exploring
## Status
Only two possible status: detected and exploring, where:
- detected: if the response of the environment focus on the location of the code piece that contains bugs and need to be patched
- exploring: if you need to more information about the project and error before 'view_code' tool can display the code piece that contain the error to be patched.'''
analyser_initial_task = '''# Tasker
## Test problem
{problem}
## Testing report
{answer}

Your task is to analyse the error and provide the code piece that contains error and need to be patched using the tool \'view_code\''''

class Analyser(EnvChat):
    modifies = ('answer', 'problems')
    system_prompt = analyser_system_prompt
    initial_task = analyser_initial_task
    code_wrap = get_tools_code()

    def exec(self, root, problems):
        problem, root, code, status = extract_sections(self.history[-1].content)[-4:]
        status = status.lower().strip()

        if status == 'detected':
            edit_code = self.history[-2].content
            return (edit_code, problems + [problem])
        return self.env.run(code, root)
