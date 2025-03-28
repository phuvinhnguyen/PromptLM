#!/bin/bash
#SBATCH --job-name=swelite_gpt_None      # Job name
#SBATCH --output=swelite_gpt_None.out    # Output file
#SBATCH --error=swelite_gpt_None.err     # Error log file
#SBATCH --time=02:00:00               # Time limit (hh:mm:ss)
#SBATCH --ntasks=1                    # Number of tasks (usually 1)
#SBATCH --cpus-per-task=4             # Number of CPU cores per task
#SBATCH --mem=16G                     # Memory per node
#SBATCH --partition=short             # Partition name (adjust based on cluster)

python -u -m GitHubAgent.experiments.swelite --token $OPENAPI --gpt

# Clone and install SWE-bench
if [ ! -d "SWE-bench" ]; then
    git clone https://github.com/SWE-bench/SWE-bench.git
fi
cd SWE-bench
pip install --quiet -e .

# Run evaluation
python -u -m swebench.harness.run_evaluation \
    --dataset_name princeton-nlp/SWE-bench_Lite \
    --predictions_path "../result/swelite_gpt_None.json" \
    --run_id validate-swelite_gpt_None \
    --modal true