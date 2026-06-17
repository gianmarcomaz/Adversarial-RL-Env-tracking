import json
from collections import Counter, defaultdict
from pathlib import Path


# Find reward files under an analysis or jobs directory.
def find_reward_files(root):
    return list(Path(root).rglob("reward.json"))


# Guess a model name from a reward file path.
def model_from_path(path):
    parts = [part for part in path.parts if "gemma" in part.lower() or "gpt" in part.lower()]
    return parts[0] if parts else "unknown"


# Load one Harbor reward file.
def load_reward(path):
    with open(path, encoding="utf-8") as file:
        return json.load(file)


# Summarize pass rates and failed checks.
def summarize(root="analysis"):
    totals = Counter()
    passes = Counter()
    failed_checks = defaultdict(Counter)

    for path in find_reward_files(root):
        reward = load_reward(path)
        model = model_from_path(path)
        totals[model] += 1
        passes[model] += int(reward.get("reward", 0))
        for name, passed in reward.get("checks", {}).items():
            if not passed:
                failed_checks[model][name] += 1

    print("model,total,passes,pass_rate,failed_checks")
    for model in sorted(totals):
        total = totals[model]
        pass_rate = round((passes[model] / total) * 100) if total else 0
        checks = "; ".join(f"{name}={count}" for name, count in failed_checks[model].items())
        print(f"{model},{total},{passes[model]},{pass_rate}%,{checks}")


# Run the summarizer from the command line.
if __name__ == "__main__":
    summarize()
