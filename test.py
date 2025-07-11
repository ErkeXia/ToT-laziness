import argparse
import time
from tot.methods.bfs import solve, get_time
from tot.tasks.game24 import Game24Task
from tot.tasks.crosswords import MiniCrosswordsTask
from tot.models import gpt_usage

task = 'crosswords'
args = argparse.Namespace(backend='gpt-3.5-turbo', temperature=0.7, task=task, naive_run=False, prompt_sample=None, method_generate='propose', method_evaluate='value', method_select='greedy', n_generate_sample=1, n_evaluate_sample=3, n_select_sample=5)
# task = Game24Task()
task = MiniCrosswordsTask()
start = time.perf_counter()
x, ys, infos, thoughts, nodes = solve(args, task, 100)
elapsed = time.perf_counter() - start
print(f"{elapsed:.6f} seconds")
print(ys[0])
# print(f"infos: {infos}")
print(gpt_usage('gpt-3.5-turbo'))
print(thoughts)
get_time() 