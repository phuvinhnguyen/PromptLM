import os
import subprocess

def create_error_project():
    # Create project directory
    project_name = "error_project"
    os.makedirs(project_name, exist_ok=True)
    os.chdir(project_name)

    # Initialize git repository
    subprocess.run(["git", "init"])

    # Create project structure with errors
    structure = {
        "src": {
            "main.py": """print("Hello World"

def calculate():
    result = 5 * 3
    return reslt
""",
            "utils.py": """def read_config()
    config = load_config()
    return config
""",
            "helper.py": """def helper_function():
for i in range(5):
print(i)
"""
        },
        "tests": {
            "test_main.py": """from srcc.main import calculate

def test_calculate():
    assert calculate() == 15
""",
            "test_utils.py": """import utils

def test_config():
    assert utils.read_config() == {}
"""
        },
        "data": {
            "sample.csv": "test,data\n1,2\n3,4"
        },
        ".gitignore": "__pycache__/\n*.log\n",
        "REAME.md": "# Error Project\nThis is a test project with intentional errors",
        "requirements.txt": "requests\nnumpy\n"
    }

    # Create files and folders
    for path, content in structure.items():
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            for file_name, file_content in content.items():
                with open(os.path.join(path, file_name), "w") as f:
                    f.write(file_content)
        else:
            with open(path, "w") as f:
                f.write(content)

    # Add all files and commit
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Initial commit with errors"])

create_error_project()

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
