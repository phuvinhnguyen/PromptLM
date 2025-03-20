import os
import json
from FlowDesign.chatbot.template import ImBot
from SCoT.SCoTD import SCoTD
from SCoT.eval.swelite import *
import argparse

class LrmBot(ImBot):
    prompt_template = '{history}<|im_start|>assistant\n<think>\n'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", type=str, help="Authentication token", default='token')
    args = parser.parse_args()
    
    result_dir = "./result"
    os.makedirs(result_dir, exist_ok=True)

    base_filename = f"experiment_{os.path.basename(__file__)}_v0.json"
    filepath = os.path.join(result_dir, base_filename)

    version = 1
    while os.path.exists(filepath):
        filepath = os.path.join(result_dir, f"experiment_{os.path.basename(__file__)}_v{version}.json")
        version += 1

    bot = LrmBot(args.token, 'Qwen/QwQ-32B', max_new_tokens=2048, device_map='auto')
    agent = SCoTD(bot)
    data = generate_patches(test_dataset, agent, 'SCoT_QwQ32b')

    # Save JSON data
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"Saved results to: {filepath}")
