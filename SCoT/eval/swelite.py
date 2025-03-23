import subprocess
import tempfile
from typing import Dict, List
from datasets import load_dataset
import json, os
from concurrent.futures import ThreadPoolExecutor

dataset = load_dataset('princeton-nlp/SWE-bench_Lite')
test_dataset = [dataset['test'][i] for i in range(len(dataset['test']))]
dev_dataset = [dataset['dev'][i] for i in range(len(dataset['dev']))]

def process_one_sample(index, data, bot, name):
    repo = data['repo']
    instance_id = data['instance_id']
    base_commit = data['base_commit']
    environment_setup_commit = data['environment_setup_commit']
    problem = data['problem_statement']

    with tempfile.TemporaryDirectory() as project_dir:
        repo_url = f"https://github.com/{repo}.git"
        try:
            subprocess.run(
                ['git', 'clone', '--quiet', repo_url, project_dir],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            print(e)
        
        try:
            subprocess.run(
                ['git', 'checkout', '--quiet', environment_setup_commit],
                cwd=project_dir,
                check=True,
                capture_output=True
            )
            
            subprocess.run(
                ['pip', 'install', '--quiet', '-e', '.'],
                cwd=project_dir,
                check=True,
                capture_output=True
            )

        except subprocess.CalledProcessError as e:
            print(e)
        
        # Checkout base commit for modifications
        subprocess.run(
            ['git', 'checkout', '--quiet', base_commit],
            cwd=project_dir,
            check=True,
            capture_output=True
        )
        
        # Run the bot to apply changes
        bot.chat(problem, project_dir)
        
        # Generate the diff against the base commit
        diff_process = subprocess.run(
            ['git', 'diff', '--no-color', 'HEAD'],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        if diff_process.returncode != 0:
            raise RuntimeError(f"Failed to generate diff: {diff_process.stderr}")
                
        # Save the result
        output = {
            "instance_id": instance_id,
            "model_patch": diff_process.stdout,
            "model_name_or_path": name
        }

        os.makedirs(f'./result/{name}', exist_ok=True)
        with open(f'./result/{name}/{instance_id}.json', 'w') as f:
            json.dump(output, f, indent=4)

        return output

def generate_patches(data_instances: list, bot, name='anonymous') -> Dict[str, List[str]]:
    def process_wrapper(index_data):
        index, data = index_data
        return process_one_sample(index, data, bot, name)

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_wrapper, enumerate(data_instances)))

    return results