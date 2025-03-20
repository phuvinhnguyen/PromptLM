import subprocess
import tempfile
from typing import Dict, List
from datasets import load_dataset
import json
import logging
import sys

# Configure logging to output to stdout with a specific format
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,  # ensures logs go to stdout
    format="%(asctime)s - %(levelname)s - %(message)s"
)

dataset = load_dataset('princeton-nlp/SWE-bench_Lite')
test_dataset = [dataset['test'][i] for i in range(len(dataset['test']))]
dev_dataset = [dataset['dev'][i] for i in range(len(dataset['dev']))]

def generate_patches(data_instances: list, bot, name='anonymous') -> Dict[str, List[str]]:
    logger = logging.getLogger()
    logger.log('-'*100)
    logger.log('generate_patches')
    results = []
    for index, data in enumerate(data_instances):
        logger.log(f'start working on data {index}: {data}')
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
                raise RuntimeError(f"Failed to clone {repo}: {e.stderr.decode()}") from e
            
            try:
                # Checkout environment setup commit
                subprocess.run(
                    ['git', 'checkout', '--quiet', environment_setup_commit],
                    cwd=project_dir,
                    check=True,
                    capture_output=True
                )
                
                try:
                    # Install dependencies
                    subprocess.run(
                        ['pip', 'install', '--quiet', '-e', '.'],
                        cwd=project_dir,
                        check=True,
                        capture_output=True
                    )
                except Exception as e:
                    print(e)
                
                # Checkout base commit for modifications
                subprocess.run(
                    ['git', 'checkout', '--quiet', base_commit],
                    cwd=project_dir,
                    check=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError as e:
                raise RuntimeError(
                    f"Environment setup failed for {instance_id}: {e.stderr.decode()}"
                ) from e
            
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
            
            my_patch_text = diff_process.stdout
            
            # Save the result
            results.append({
                "instance_id": instance_id,
                "model_patch": my_patch_text,
                "model_name_or_path": name
            })

            # Log and save result in case of unexpected errors
            print('    <>' * 12)
            print(f'# Finish generating patch for data {index}: {instance_id}')
            print(results[-1])

            with open(f'experiment_log_{name}.json', "w", encoding="utf-8") as file:
                json.dump(results, file, indent=4, ensure_ascii=False)
            
    return results