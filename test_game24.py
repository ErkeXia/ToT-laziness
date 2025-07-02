import argparse
import sys
from tot.methods.bfs import solve, get_time
from tot.tasks.game24 import Game24Task
from tot.models import gpt_usage, reset
import json
from tqdm import tqdm
from contextlib import redirect_stdout


model = 'gpt-4'
args = argparse.Namespace(backend=model, temperature=0.7, task='game24', naive_run=False, prompt_sample=None, method_generate='propose', method_evaluate='value', method_select='greedy', n_generate_sample=1, n_evaluate_sample=3, n_select_sample=5)

task = Game24Task()
def test_game24_range(start=400, end=449):
    for i in tqdm(range(start, end + 1), desc="Testing Game24"):
        reset()
        x, ys, infos, thoughts = solve(args, task, i)
        stats = gpt_usage(model)
        propose_num, value_num, propose_avg, value_avg = get_time()
        result = {
            "seed": i,
            "x": x,
            "answer": ys[0],
            "infos": infos,
            "thoughts": thoughts,
            "prompt_tokens": stats["prompt_tokens"],
            "completion_tokens": stats["completion_tokens"],
            "propose_num": propose_num,
            "value_num": value_num,
            "propose_avg": propose_avg,
            "value_avg": value_avg
        }
        with open("gpt4_results.jsonl", "a") as f:
            f.write(json.dumps(result) + "\n")
test_game24_range()
# with open("gpt4_results.json", "w") as f:
#     json.dump(results, f, indent=2)
