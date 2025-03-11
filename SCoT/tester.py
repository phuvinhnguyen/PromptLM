from SCoT.envchat import *
from SCoT.utils import *

tester_system_prompt = f'''# Tools
{get_tools_description()}
# Task
You are a tester that will discover and create a test script to check if the provided problem is still persisted in the given project. Tasker will give you information about the problem and the project. Your program, which can be testing program, project discovering program, or installing dependencies to run your test program, will be executed and returned by the Environment. You must strictly follow the output format as provided below.
# Output format:
## Thinking
Your step by step thinking on how to discovering and write a test program
## Execution path
/path/to/the/directory/that/the/program/will/be/run/at
## Program
A python program that can be executed to discover the project or print out errors, logs and provide detailed information if the problem is still persisted. Your Python program can use build-in tools are provided in the Tools section (code of each tool will be inserted to your code automatically before executing).
## Status
One of the following: bugs, fixed, discovering. Where:
- bugs: use when the previous return from your program shows that the bug is still existed in the project
- fixed: use when the return shows that the bug is completely fixed. You should check this 1 or 2 times to ensure this case
- discovering: use when your program is used to discover the project, including existing test cases, unit tests'''
tester_initial_task = '''# Tasker
## The project can be found at
{root}
## This is the problem that you need to check
{problem}
## This is the search results for some possible unit tests in the project
{answer} '''
tester_bug_prompt = '''The test program is executed at: {root}
## Testing code
{code}
## Reported logs and bugs
{env}'''

class Tester(EnvChat):
    system_prompt = tester_system_prompt
    initial_task = tester_initial_task
    modifies = ('answer', 'problems', )
    code_wrap = get_tools_code()

    def exec(self, root, problems):
        root, code, status = extract_sections(self.history[-1].content)[-3:]
        status = status.lower().strip()
        if status == 'bugs':
            root, code, status = extract_sections(self.history[-3].content)[-3:]
            return (tester_bug_prompt.format(code=code, env=self.history[-2].content, root=root.strip()), True)
        elif status == 'fixed':
            return ('', False)
        return self.env.run(code, root.strip())
    
    def process(self, problems, root, test_root):
        while problems != []:
            answers = super().process(test_root, problems, root)
            if len(answers) == 2:
                answer, stop = answers
            else:
                answer = answers[0]
                break
            if stop: break
            problems = problems[:-1]
        return (answer, problems)