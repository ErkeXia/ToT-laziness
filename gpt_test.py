from tot.models import gpt
from tot.methods.bfs import get_value
from tot.tasks.game24 import Game24Task
from functools import partial

import sys
import time

propose_prompt = '''You aim to use numbers and basic arithmetic operations (+ - * /) to obtain 24.
You now should provide eight possible next steps for the given input like the example.
EXAMPLE:
Input: 2 8 8 14
Possible next steps:
2 + 8 = 10 (left: 8 10 14)
8 / 2 = 4 (left: 4 8 14)
14 + 2 = 16 (left: 8 8 16)
2 * 8 = 16 (left: 8 14 16)
8 - 2 = 6 (left: 6 8 14)
14 - 8 = 6 (left: 2 6 8)
14 /  2 = 7 (left: 7 8 8)
14 - 2 = 12 (left: 8 8 12)
TASK:
Input: 4 5 6 10
Possible next steps:
'''

value_prompt = '''Evaluate if given numbers can reach 24 (sure/likely/impossible)
10 14
10 + 14 = 24
sure
11 12
11 + 12 = 23
12 - 11 = 1
11 * 12 = 132
11 / 12 = 0.91
impossible
4 4 10
4 + 4 + 10 = 8 + 10 = 18
4 * 10 - 4 = 40 - 4 = 36
(10 - 4) * 4 = 6 * 4 = 24
sure
4 9 11
9 + 11 + 4 = 20 + 4 = 24
sure
5 7 8
5 + 7 + 8 = 12 + 8 = 20
(8 - 5) * 7 = 3 * 7 = 21
I cannot obtain 24 now, but numbers are within a reasonable range
likely
5 6 6
5 + 6 + 6 = 17
(6 - 5) * 6 = 1 * 6 = 6
I cannot obtain 24 now, but numbers are within a reasonable range
likely
10 10 11
10 + 10 + 11 = 31
(11 - 10) * 10 = 10
10 10 10 are all too big
impossible
1 3 3
1 * 3 * 3 = 9
(1 + 3) * 3 = 12
1 3 3 are all too small
impossible
4 4 5
'''
x = "4 5 6 10"
y = "4 + 5 = 9 (left: 9 10)"
task = Game24Task()
start = time.perf_counter()
# global gpt
# gpt = partial(gpt, model="gpt-4", temperature=0.7)
for i in range(1):
    print(x)
    value_outputs = gpt(propose_prompt, model="gpt-4.1", n=1, stop=None)
    # value = task.value_outputs_unwrap(x, y, value_outputs)
    print(value_outputs)
    # .split('\n')
    # proposals = [s for s in proposals if not ("Input" in s or "steps" in s)]
    # value = get_value(Game24Task(), x, y, 1, cache_value = False)
    # print(value)
elapsed = time.perf_counter() - start
print(f"{elapsed:.6f} seconds")
# print(value)