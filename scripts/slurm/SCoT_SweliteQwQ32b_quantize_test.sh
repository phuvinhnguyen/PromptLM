#!/bin/bash
#SBATCH --job-name=swebench_eval      # Job name
#SBATCH --output=swebench_eval.out    # Output file
#SBATCH --error=swebench_eval.err     # Error log file
#SBATCH --time=02:00:00               # Time limit (hh:mm:ss)
#SBATCH --ntasks=1                    # Number of tasks (usually 1)
#SBATCH --cpus-per-task=4             # Number of CPU cores per task
#SBATCH --mem=16G                     # Memory per node
#SBATCH --gres=gpu:1                   # Request 1 GPU (remove if not needed)
#SBATCH --partition=amperenodes           # Partition name (adjust based on cluster)

# Load necessary modules (adjust for your environment)
module load python/3.10
module load git

curl -L https://ollama.com/download/ollama-linux-amd64.tgz -o ollama-linux-amd64.tgz
mkdir -p ~/.bin/ollama
tar -C ~/.bin/ollama -xzf ollama-linux-amd64.tgz
echo 'export PATH=$PATH:~/.bin/ollama' >> ~/.bashrc
. ~/.bashrc
ollama pull qwq
python -m SCoT.experiments.Swelite_QwQ32b_quantize_test

# Clone and install SWE-bench
if [ ! -d "SWE-bench" ]; then
    git clone https://github.com/SWE-bench/SWE-bench.git
fi
cd SWE-bench
pip install -e .

# Run evaluation
python -m swebench.harness.run_evaluation \
    --dataset_name princeton-nlp/SWE-bench_Lite \
    --predictions_path "../result/experiment_Swelite_QwQ32b_quantize_test_v0.json" \
    --run_id validate-Swelite_QwQ32b_test \
    --modal true