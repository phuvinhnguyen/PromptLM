import os
from FlowDesign.chatbot import *
from SCoT.SCoTD import SCoTD
from SCoT.eval.swelite import *
import argparse

def merge_json(input_folder, output_file):
    data = [json.load(open(os.path.join(input_folder, f), encoding="utf-8")) 
            for f in os.listdir(input_folder) if f.endswith(".json")]
    json.dump(data, open(output_file, "w", encoding="utf-8"), indent=4, ensure_ascii=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", type=str, help="Authentication token", default='token')
    args = parser.parse_args()
    
    result_dir = "./result"
    name = os.path.basename(__file__)
    os.makedirs(result_dir, exist_ok=True)

    bot = ChatGPTbot(args.token)
    agent = SCoTD(bot)
    data = generate_patches(dev_dataset[:3], agent, f'{name}')

    merge_json(f'./result/{name}', f'./result/{name}.json')