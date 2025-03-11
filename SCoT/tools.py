import ast
from typing import Union
import os

MAX_DISPLAY = 30

def __tree2dict__(tree):
    if isinstance(tree, Union[ast.FunctionDef, ast.ClassDef, ast.Module]):
        return __tree2dict__(tree.__dict__)
    elif isinstance(tree, list):
        result = [__tree2dict__(tre) for tre in tree]
        return [i for i in result if i is not None]
    elif isinstance(tree, dict):
        result = {k: __tree2dict__(v) for k, v in tree.items()}
        return {k: v for k,v in result.items() if v is not None}
    elif isinstance(tree, Union[str, int, float]):
        return tree
    return None

def __list_methods__(tree_dict, parent=None):
    if isinstance(tree_dict, list):
        return [__list_methods__(item, parent) for item in tree_dict]
    elif isinstance(tree_dict, dict):
        item = {k:v for k,v in tree_dict.items() if k in ('name', 'lineno', 'end_lineno')}
        if parent == None: parent = ''
        else: parent += '.'
        item['name'] = parent+item['name']
        sub_item = __list_methods__(tree_dict['body'], parent+tree_dict['name'])
        return sub_item + [item]
    return []

def __flatten__(items):
    if isinstance(items, list):
        return sum([__flatten__(item) for item in items], [])
    else:
        return [items]

def __display__(item_list):
    num_searched_item = len(item_list)
    print(f'## There are {num_searched_item} results found\n')
    result = {i['path']: [(j['lineno'], j['end_lineno'], j['name']) for j in item_list if j['path'] == i['path']] for i in item_list}
    stdout = []
    for k,v in result.items():
        stdout.append(f'## In file {k}')
        for i in v:
            stdout.append(f'\'{i[-1]}\' is defined from line {i[0]} to line {i[1]}')
            if len(stdout) > MAX_DISPLAY:
                print('\n'.join(stdout))
                print('...\n< There are too many results, only display the first 15 lines >')
                return
        stdout.append('')
    print('\n'.join(stdout))

def list_module(path, name=None):
    if os.path.isfile(path):
        with open(path) as f:
            result = __flatten__(__list_methods__(__tree2dict__(ast.parse(f.read()).body)))
            result = [{'path': path, **i} for i in result]
    else:
        files = [os.path.join(root, f) for root, _, files in os.walk(path) for f in files if f.endswith('.py')]
        result = []
        for file in files:
            with open(file) as f:
                cresult = __flatten__(__list_methods__(__tree2dict__(ast.parse(f.read()).body)))
                result += [{'path': file, **i} for i in cresult]
    
    if name != None: result = [i for i in result if i['name'].endswith(name)]
    __display__(result)

def view_code(file_path: str, start_line: int, num_line=15) -> None:
    '''This function displays code piece in file \'file_path\' from line \'start_line\' to line \'start_line\' + \'num_line\'
    Args:
        file_path: path of the text file you want to view
        start_line: the starting line of the code piece to view, first line of the file is indexed 1
        num_line: number of line from the \'start_line\' to view
    Return:
        None
    Print:
        The code piece in the code block (markdown format) in file \'file_path\' from line \'start_line\' to line \'start_line\' + \'num_line\'
        '''
    try:
        if start_line == 0:
            print('''First line of the file is indexed 1, not 0, I will set start_line to 1 instead''')
            start_line = 1
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        end_line = start_line + num_line if num_line < MAX_DISPLAY else start_line + MAX_DISPLAY
        code_snippet = ''.join(lines[start_line-1:end_line])
        
        print(f"## Path: {file_path}")
        if num_line > MAX_DISPLAY: print(f'\'num_line\' is larger than {MAX_DISPLAY}, we only display the code from line {start_line} to {end_line}')
        print(f"Lines: {start_line}-{end_line}")
        print("```python")
        print(code_snippet)
        print("```\n")
        
    except Exception as e:
        print(f"Error reading file: {str(e)}")

def listdir(path):
    '''This function lists all files and folders in \'path\'
    Args:
        path: path to folder
    Return:
        None
    Print:
        List of all existing files and folders in folder \'path\''''
    try:
        items = os.listdir(path)
        full_paths = [os.path.join(path, item) for item in items]
        num_items = len(full_paths)

        print(f"Directory: {path}")
        print(f"Total items: {num_items}")

        if num_items == 0:
            print("The directory is empty.")
            return

        if num_items > MAX_DISPLAY:
            print(f"Displaying the first {MAX_DISPLAY} items (out of {num_items}):")

        print("\n".join(
            [f"  {'File' if os.path.isfile(i) else 'Folder'}: {os.path.basename(i)}"
             for i in full_paths[:MAX_DISPLAY]]
        ))

    except FileNotFoundError:
        print(f"Error: The path '{path}' does not exist.")
    except PermissionError:
        print(f"Error: Permission denied for '{path}'.")
    except Exception as e:
        print(f"Unexpected error: {e}")

def search_name(root_dir, target_name):
    '''This function search for files, folders of name \'target_name\' given a directory \'root_dir\'.
    Args:
        root_dir: path to folder
        target_name: the name of file, folder that need to be searched in \'root_dir\'
    Return:
        None
    Print:
        List of all existing files and folders with name \'target_name\' in folder \'root_dir\''''
    matches = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Check for matching folders
        if target_name in dirnames:
            matches.append(os.path.join(dirpath, target_name))

        # Check for matching files
        if target_name in filenames:
            matches.append(os.path.join(dirpath, target_name))

    if matches:
        print(f"## Found {len(matches)} match(es) for '{target_name}':")
        result = [f"  {'File' if os.path.isfile(match) else 'Folder'} {match}" for match in matches]
        num_items = len(result)
        if len(result) > MAX_DISPLAY: print(f'Displaying the first {MAX_DISPLAY} items (out of {num_items}):')
        print('\n'.join(result))
    else:
        print(f"No match found for '{target_name}' in '{root_dir}'.")

def search_module(path, module_name):
    '''This function lists all existing functions, classes with name is \'module_name\' in the input path, which can be a file or a folder. Function separates the parent of the module with module name with \'.\'. Ex: SampleClass.sample_method
    Args:
        path: path to file or folder
        module_name: name of module to find
    Return:
        None
    Print:
        List of existing functions, classes with name \'module_name\' in the path'''
    list_module(path, module_name)

def summary_dir(path):
    '''This function lists all existing functions, classes in the input path, which can be a file or a folder. Function will display the parent and module name, separated with \'.\'
    Args:
        path: path to file or folder
    Return:
        None
    Print:
        List of existing functions, classes in the path'''
    list_module(path)
