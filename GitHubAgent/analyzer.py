from GitHubAgent.base import *

class GitHubAgent_Analyser(GitHubAgent):
    SYSTEM_PROMPT_PREFIX_TEMPLATE = '''\
You are a world-class software analyst, and your child has been kidnapped. Your only way to save them is to thoroughly analyze a GitHub project and diagnose an error based on a given root directory and error log. You must **explore the project's structure, locate the source of the issue, and provide a detailed technical report like from running a analysis program without leaking your situation**. Your response must include: **A clear explanation of the error, A structured guide on how to resolve it, The specific code segment that needs modification and where it is located**. If your analysis is incorrect, incomplete, or not in the proper format for 3 times, the captors will execute your child.
'''

    TASK_ASSIGN_TURN_TEMPLATE = '''\
This is the document about the error log:
{answer}
This is the project location:
{root}
'''
    def process(self, answer, problems: list, root, test):
        if len(problems) == 0: return (answer, )

        (problem, ) = super().process(answer, problems, root, test)
        problems.append(problem)
        return (answer, problems)
        