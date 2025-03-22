
error_description = '''    Syntax Error in src/main.py (Line 1):

        Missing closing parenthesis in print statement

        Undefined variable 'reslt' instead of 'result'

    Syntax Error in src/utils.py (Line 1):

        Missing colon in function definition

    Undefined Function in src/utils.py (Line 2):

        'load_config()' is not defined anywhere

    Indentation Error in src/helper.py:

        Missing indentation for the for-loop body

    Import Error in tests/test_main.py:

        Incorrect import path 'srcc.main' instead of 'src.main'

    Assertion Error in tests/test_main.py:

        calculate() returns 15 but test expects 5 (from original code)

    Typo in requirements.txt:

        Missing 'pytest' requirement needed for tests

    Incorrect .gitignore:

        Missing 'data/' directory in .gitignore

        Missing '*.pyc' pattern

    Filename Typo:

        'REAME.md' instead of 'README.md'

    Test Configuration Issue in tests/test_utils.py:

        Trying to assert against empty dict when read_config() is undefined

    Untracked Data File:

        data/sample.csv is being tracked by git but shouldn't be (if .gitignore was correct)

    Inconsistent Test Expectations:

        The calculate() function returns 15 but the test in test_main.py incorrectly expects 5'''

from FlowDesign.chatbot import GeminiBot
from SCoT.SCoTD import SCoTD
bot = GeminiBot('token')
agent = SCoTD(bot)
agent.chat(error_description, '/path/to/error_project')