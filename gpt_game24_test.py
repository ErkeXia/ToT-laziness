import argparse
import sys
from tot.methods.bfs import solve, get_time
from tot.tasks.game24 import Game24Task
from tot.models import gpt_usage, reset
import json
import time
from tqdm import tqdm
from contextlib import redirect_stdout


model = 'gpt-4.1-mini'
args = argparse.Namespace(backend=model, temperature=0.7, task='game24', naive_run=False, prompt_sample=None, method_generate='propose', method_evaluate='value', method_select='greedy', n_generate_sample=1, n_evaluate_sample=3, n_select_sample=5)
task = Game24Task()

def test_game24_gpt(start=351, end=400):
    for i in tqdm(range(start, end + 1), desc="Testing lazy"):
        reset()
        start = time.perf_counter()
        with open(f"logs/game24_gpt4_1/solve_output_seed_{i}.txt", "w") as log_file:  # You can also just use "solve_output.txt"
            with redirect_stdout(log_file):
                x, ys, infos, thoughts, nodes_num = solve(args, task, i)
        elapsed = time.perf_counter() - start
        gpt_stats = gpt_usage(model)
        propose_num, value_num, propose_avg, value_avg = get_time()
        result = {
            "seed": i,
            "x": x,
            "answer": ys[0],
            "thoughts": thoughts,
            "gpt_prompt_tokens": gpt_stats["prompt_tokens"],
            "gpt_completion_tokens": gpt_stats["completion_tokens"],
            "propose_num": propose_num,
            "value_num": value_num,
            "propose_avg": propose_avg,
            "value_avg": value_avg,
            "total_time": elapsed,
            "nodes": nodes_num,
            "infos": infos
        }
        with open("gpt_4_1_game24_results.jsonl", "a") as f:
            f.write(json.dumps(result) + "\n")
            
test_game24_gpt()