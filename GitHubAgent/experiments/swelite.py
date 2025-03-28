import os
import json
import argparse
from eval.swelite import *
from GitHubAgent.agentv1 import GitHubAgentv1
from FlowDesign.chatbot import ChatGPTbot, GeminiBot, HuggingFacebot, ImBot

def merge_json(input_folder, output_file):
    """Merge all JSON files in a folder into a single JSON file."""
    data = []
    if os.path.exists(input_folder) and os.path.isdir(input_folder):
        for f in os.listdir(input_folder):
            if f.endswith(".json"):
                with open(os.path.join(input_folder, f), encoding="utf-8") as file:
                    data.append(json.load(file))

    with open(output_file, "w", encoding="utf-8") as out_file:
        json.dump(data, out_file, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", type=str, help="Authentication token", default='token')
    parser.add_argument("--gpt", action='store_true', help="Use GPT API")
    parser.add_argument("--gemini", action='store_true', help="Use Gemini API")
    parser.add_argument("--hg", action='store_true', help="Use Hugging Face API")
    parser.add_argument("--fnc_call", action='store_true', help="Use built-in function-call")
    parser.add_argument("--name", type=str, help="Model name", default=None)
    args = parser.parse_args()

    result_dir = "./result"
    os.makedirs(result_dir, exist_ok=True)

    bot = None  # Default bot
    if args.gpt:
        bot = ChatGPTbot(args.token, model_name=args.name) if args.name else ChatGPTbot(args.token)
        name = f'_gpt_{args.name}'
    elif args.gemini:
        bot = GeminiBot(args.token, model_name=args.name) if args.name else GeminiBot(args.token)
        name = f'_gemini_{args.name}'
    elif args.hg:
        bot = HuggingFacebot(args.token, model_repo_id=args.name, run_local=True) if args.name else HuggingFacebot(args.token)
        name = f'_huggingface_{args.name}'

    if bot is None:
        raise ValueError("No bot selected. Use --gpt, --gemini, or --hg.")

    if args.fnc_call:
        agent = GitHubAgentv1(bot, repeat=4, history_limit=5, loop_time=1, builtin_fnc_call=True)
    else:
        agent = GitHubAgentv1(bot, repeat=4, history_limit=5, loop_time=1)

    if not dev_dataset:
        raise ValueError("Error: `dev_dataset` is empty. Load valid data before running.")

    # Generate patches
    script_name = os.path.splitext(os.path.basename(__file__))[0] + name # Remove .py extension
    output_folder = os.path.join(result_dir, script_name)

    os.makedirs(output_folder, exist_ok=True)

    data = generate_patches(test_dataset, agent, script_name)

    # Merge JSON files
    merge_json(output_folder, os.path.join(result_dir, f"{script_name}.json"))
