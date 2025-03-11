#!/bin/bash

curl -fsSL https://ollama.com/install.sh | sh
ollama run qwq
python -m SCoT.experiments.Swelite_QwQ32b_quantize_test
ollama stop qwq

git clone https://github.com/SWE-bench/SWE-bench.git
cd SWE-bench
pip install -e .

python -m swebench.harness.run_evaluation \
    --dataset_name princeton-nlp/SWE-bench_Lite \
    --predictions_path "../result/experiment_Swelite_QwQ32b_quantize_test_v0.json" \
    --run_id validate-Swelite_QwQ32b_quantize_test \
    --modal true
