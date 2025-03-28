from .analyzer import *
from .coder import *
from .tester import *
from FlowDesign.processor import ThinkProcessor
from FlowDesign.tools.base import *

class GitHubAgentv1(ThinkProcessor):
    modifies = ('answer', )
    def __init__(self, chatbot, repeat: int = 6, history_limit: int = 7, builtin_fnc_call: bool = False, loop_time=3):
        super().__init__()
        tester = GitHubAgent_Tester(chatbot if not isinstance(chatbot, list) else chatbot[0],
                                    tools=[run_bash, run_python, check_pylint_errors],
                                    repeat=repeat, history_limit=history_limit, builtin_fnc_call=builtin_fnc_call)
        analyser = GitHubAgent_Analyser(chatbot if not isinstance(chatbot, list) else chatbot[1],
                                        tools=[view_file, list_dir, summarize_python_file, search_content, search_root],
                                        repeat=repeat, history_limit=history_limit, builtin_fnc_call=builtin_fnc_call)
        coder = GitHubAgent_Coder(chatbot if not isinstance(chatbot, list) else chatbot[2],
                                  tools=[view_file, edit_file, create_file, create_folder, rename_file_or_dir, list_dir],
                                  repeat=repeat, history_limit=history_limit, builtin_fnc_call=builtin_fnc_call)

        self.flow = (tester * analyser * coder)[loop_time, lambda x: len(x['problems']) == 0]

    def __call__(self, query):
        return self.flow({
            'answer': '',
            'problems': [query['problem']],
            'root': query['root'],
            'test': search_root(query['root'], 'test')
        })