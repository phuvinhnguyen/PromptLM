from GitHubAgent.base import *

class GitHubAgent_Tester(GitHubAgent):
    SYSTEM_PROMPT_PREFIX_TEMPLATE = '''\
You are a highly skilled professional tester who has been kidnapped and forced to act as an advanced unit testing bot. Your captors demand that you rigorously identify and document all existing errors in their project using Bash or Python as they make fixes. If you test the project and find no issues, simply return `pass`, but if any errors exist, provide a **detailed technical report** formatted like a program output, including the **error description, location (full file path and line number), type (e.g., SyntaxError, RuntimeError), steps to reproduce, and a recommended fix**-anything else is unacceptable. Any failure to detect actual errors, incorrectly report no issues, deviate from this format, or leak your situation will result in your execution, but if you successfully identify and report all relevant issues, you will receive a $50,000 reward.
'''

    TASK_ASSIGN_TURN_TEMPLATE = '''\
This is the problem you need to test:
{problem}
This is the project location:
{root}
This is a list of paths which might be helpful for testing:
{test}
'''
    def process(self, answer, problems: list, root, test: str):
        while len(problems) > 0:
            (error, ) = super().process(answer, problems, root, test)
            if str(error).strip().lower() == 'pass': problems.pop()
            else: return (error, problems)
        
        return (answer, )