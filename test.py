import argparse
import time
from tot.methods.bfs import solve, get_time
from tot.tasks.game24 import Game24Task
from tot.models import gpt_usage


args = argparse.Namespace(backend='gpt-4.1-mini', temperature=0.7, task='game24', naive_run=False, prompt_sample=None, method_generate='propose', method_evaluate='value', method_select='greedy', n_generate_sample=1, n_evaluate_sample=3, n_select_sample=5)
task = Game24Task()
start = time.perf_counter()
x, ys, infos, thoughts = solve(args, task, 710)
elapsed = time.perf_counter() - start
print(f"{elapsed:.6f} seconds")
print(ys[0])
# print(f"infos: {infos}")
print(gpt_usage('gpt-4'))
print(thoughts)
get_time() 