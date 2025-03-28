#!/bin/bash
#SBATCH --job-name=swebench_eval      # Job name
#SBATCH --output=swebench_eval.out    # Output file
#SBATCH --error=swebench_eval.err     # Error log file
#SBATCH --time=02:00:00               # Time limit (hh:mm:ss)
#SBATCH --ntasks=1                    # Number of tasks (usually 1)
#SBATCH --cpus-per-task=4             # Number of CPU cores per task
#SBATCH --mem=16G                     # Memory per node
#SBATCH --partition=amperenodes       # Partition name (adjust based on cluster)

python -u -m GitHubAgent.experiments.swelite --token $OPENAPI --gpt

# # Clone and install SWE-bench
# if [ ! -d "SWE-bench" ]; then
#     git clone https://github.com/SWE-bench/SWE-bench.git
# fi
# cd SWE-bench
# pip install --quiet -e .

# # Run evaluation
# python -u -m swebench.harness.run_evaluation \
#     --dataset_name princeton-nlp/SWE-bench_Lite \
#     --predictions_path "../result/Swelite_gpt4omini_test.py.json" \
#     --run_id validate-Swelite_gpt4omini_test \
#     --modal true