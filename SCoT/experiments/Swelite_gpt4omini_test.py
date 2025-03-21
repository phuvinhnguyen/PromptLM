import os
import json
from FlowDesign.chatbot import *
from SCoT.SCoTD import SCoTD
from SCoT.eval.swelite import *
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", type=str, required=True, help="Authentication token", default='token')
    args = parser.parse_args()

    bot = ChatGPTbot(args.token)
    agent = SCoTD(bot)
    name = os.path.basename(__file__)
    data = generate_patches(test_dataset[:1], agent, f'{name}')
    
    # Ensure the folder exists
    result_dir = "./result"
    os.makedirs(result_dir, exist_ok=True)

    # Base filename
    base_filename = f"experiment_{name}_v0.json"
    filepath = os.path.join(result_dir, base_filename)

    # If file exists, create a new version
    version = 1
    while os.path.exists(filepath):
        filepath = os.path.join(result_dir, f"experiment_{name}_v{version}.json")
        version += 1

    # Save JSON data
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"Saved results to: {filepath}")
