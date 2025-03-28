from SCoT.analyser import Analyser
from SCoT.coder import Coder
from SCoT.tester import Tester
from SCoT.utils import search_name_similar
from FlowDesign.processor import ThinkProcessor

class SCoT(ThinkProcessor):
    def __init__(self, bot):
        super().__init__()
        max_time = 12
        max_history = 14
        repeat = 5
        coder = Coder(bot, max_time=max_time, max_history=max_history)
        analyser = Analyser(bot, max_time=max_time, max_history=max_history)
        tester = Tester(bot, max_time=max_time, max_history=max_history)
        self.flow = (tester * analyser * coder)[repeat, lambda x: len(x['problems']) == 0]

    def __call__(self, query: dict):
        return self.flow(query)
    
    def chat(self, problem, root):
        return self.__call__(dict(
            answer='',
            problems=[problem],
            root=root,
            test_root=search_name_similar(root, 'test')
        ))