import argparse
import sys
from tot.methods.bfs import solve
from tot.tasks.game24 import Game24Task
from tot.models import gpt_usage
import json
from tqdm import tqdm
from contextlib import redirect_stdout


model = 'gpt-4'
args = argparse.Namespace(backend=model, temperature=0.7, task='game24', naive_run=False, prompt_sample=None, method_generate='propose', method_evaluate='value', method_select='greedy', n_generate_sample=1, n_evaluate_sample=3, n_select_sample=5)

task = Game24Task()
def test_game24_range(start=800, end=810):
    results = []
    for i in tqdm(range(start, end + 1), desc="Testing Game24"):
        with open("solve_v1_output.log", "a") as f, redirect_stdout(f):
            ys, infos = solve(args, task, i)
            print(ys[0])        
    return results
results = test_game24_range()
with open("results.json", "w") as f:
    json.dump(results, f, indent=2)
