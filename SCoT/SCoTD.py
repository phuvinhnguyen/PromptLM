from SCoT.analyser import Analyser
from SCoT.dcoder import DirectCoder
from SCoT.tester import Tester
from SCoT.utils import search_name_similar
from FlowDesign.processor import ThinkProcessor

class SCoTD(ThinkProcessor):
    def __init__(self, bot):
        super().__init__()
        coder = DirectCoder(bot)
        analyser = Analyser(bot)
        tester = Tester(bot)
        self.flow = (tester * analyser * coder)[5, lambda x: len(x['problems']) == 0]

    def __call__(self, query: dict):
        return self.flow(query)
    
    def chat(self, problem, root):
        return self.__call__(dict(
            answer='',
            problems=[problem],
            root=root,
            test_root=search_name_similar(root, 'test')
        ))