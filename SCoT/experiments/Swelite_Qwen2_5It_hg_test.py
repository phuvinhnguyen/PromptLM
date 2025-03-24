import os
import json
from FlowDesign.chatbot.template import ImBot
from SCoT.SCoTD import SCoTD
from SCoT.eval.swelite import *
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", type=str, help="Authentication token", default='token')
    args = parser.parse_args()
    
    result_dir = "./result"
    name = os.path.basename(__file__)
    os.makedirs(result_dir, exist_ok=True)
    base_filename = f"experiment_{name}_v0.json"
    filepath = os.path.join(result_dir, base_filename)

    bot = ImBot(args.token, run_local='hg', device_map='auto', pipeline_kwargs={'max_new_tokens': 2024}, batch_size=64)
    agent = SCoTD(bot)
    data = generate_patches(test_dataset, agent, f'{name}')