from FlowDesign.processor.base import *
import subprocess
from SCoT.utils import *

default_env_prompt = '''# Environment
## Program is executed at
{root}
## Program's output
{stdout}
## Program's error
{stderr}'''
default_wrong_format_answer = '''# Environment
Your answer is in the wrong format, I cannot detect correct parts to run. Please provide the answer again but in the correct format as defined by system.'''
default_code_wrap = ''

class Environment:
    def __init__(self, env_prompt=None, code_wrap=None):
        self.process = {
            'python': ["python3", "-c"],
            'bash': ["bash", "-c"],
            'javascript': ["node", "-e"],
            'ruby': ["ruby", "-e"],
            'perl': ["perl", "-e"],
            '': ["python3", "-c"],
        }
        self.prompt = env_prompt
        self.code_wrap = code_wrap

    def get_code(self, markdown_text):
        return extract_code(markdown_text)
    
    def run(self, text, root):
        print('* '*20, 'Env', '* ' * 20)
        try:
            lang, code = self.get_code(text)
            code = self.code_wrap + code
            output = subprocess.run(self.process[lang.lower()] + [code], cwd=root, capture_output=True, text=True, timeout=10)
            output = self.prompt.format(root=root, stdout=output.stdout, stderr=output.stderr)
        except Exception as e:
            output = 'Environment has some problems running the code:\n' + str(e)
        print(output)
        print('* '*20, 'Env', '* ' * 20)
        return output

class EnvChat(ChatProcessor):
    modifies = ('answer', )
    system_prompt = ''
    initial_task = ''
    env_prompt = default_env_prompt
    code_wrap = default_code_wrap

    def __init__(self, chatbot, max_time=10, max_history=12):
        super().__init__(chatbot)
        self.history = History()
        self.history.system(self.system_prompt)
        self.max_time = max_time
        self.max_history = max_history
        self.env = Environment(self.env_prompt, self.code_wrap)

    def task(self, answer, problem, root): return self.initial_task.format(answer=answer, problem=problem, root=root)
    
    def exec(self, root, problems): return ''

    def process(self, answer, problems, root):
        if len(problems) == 0: return ()

        print('='*15, self.__class__, '='*15)
        answer = self.task(answer, problems[-1], root)
        for _ in range(self.max_time):
            print(self.history[-1].content)
            print('    <>'*16)
            super().process(answer, self.history)[0]
            try:
                answer = self.exec(root, problems)
            except:
                answer = default_wrong_format_answer

            if len(self.history) > self.max_history:
                self.history = History([self.history[0]] + self.history[-self.max_history:])
            if isinstance(answer, tuple): break
        return answer if isinstance(answer, tuple) else (answer, )
