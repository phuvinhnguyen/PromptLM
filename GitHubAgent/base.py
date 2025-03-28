from FlowDesign.flow import Agent

class GitHubAgent(Agent):
    SYSTEM_PROMPT_PREFIX_TEMPLATE = None
    TASK_ASSIGN_TURN_TEMPLATE = None
    modifies = ('answer', 'problems')

    def __init__(self, chatbot, tools = ..., repeat=6, history_limit=7, builtin_fnc_call=False):
        super().__init__(chatbot, self.SYSTEM_PROMPT_PREFIX_TEMPLATE, tools, repeat, history_limit, builtin_fnc_call)

    def process(self, answer, problems, root, test):
        if len(problems) == 0: return (answer, )
        
        output = super().process(self.TASK_ASSIGN_TURN_TEMPLATE.format(
            answer=answer,
            problem=problems[-1],
            root=root,
            test=test,
        ))

        print('-'*20, self, '-'*20)
        print(output[0])
        print('-'*20, 'END OF', self, '-'*20)
        print()

        return output