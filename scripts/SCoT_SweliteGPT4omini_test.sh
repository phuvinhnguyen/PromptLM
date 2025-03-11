#!/bin/bash

python -m SCoT.experiments.Swelite_gpt4omini_test --token $RUNNINGAPI

git clone https://github.com/SWE-bench/SWE-bench.git
cd SWE-bench
pip install -e .

python -m swebench.harness.run_evaluation \
    --dataset_name princeton-nlp/SWE-bench_Lite \
    --predictions_path "../result/experiment_Swelite_gpt4omini_test_v0.json" \
    --run_id validate-Swelite_gpt4omini_test \
    --modal true