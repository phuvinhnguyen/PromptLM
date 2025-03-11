#!/bin/bash

python -m SCoT.experiments.Swelite_gemini_15_flash_test --token $RUNNINGAPI

git clone https://github.com/SWE-bench/SWE-bench.git
cd SWE-bench
pip install -e .

python -m swebench.harness.run_evaluation \
    --dataset_name princeton-nlp/SWE-bench_Lite \
    --predictions_path "../result/experiment_Swelite_gemini_15_flash_test_v0.json" \
    --run_id validate-Swelite_gemini_15_flash_test \
    --modal true