from tot.models import gpt
from tot.methods.bfs import get_value, get_values
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
6 10 8
'''

propose_gpt_4_1 = '''
You aim to use numbers and basic arithmetic operations (+ - * /) to obtain 24.
You now should provide eight possible next steps for the given input in the exact format shown in examples.
EXAMPLE1:
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
EXAMPLE2:
Input: 2 12
Possible next steps:
2 * 12 = 24 (left: 24)
2 + 12 = 14 (left: 14)
12 - 2 = 10 (left: 10)
2 - 12 = -10 (left: -10)
12 / 2 = 6 (left: 6)
12 + 2 = 14 (left: 14)
12 * 2 = 24 (left: 24)
2 / 12 = 0.17 (left: 0.17)
TASK:
Input: 4 5 6 10
Possible next steps:
'''

x = "6 8 10 13"
y = "13 - 5 = 8 (left: 6 8 10)  \n6 + 8 = 14 (left: 14 10)\n14 + 10 = 24 (left: 24)\n13 - 5 = 8 (left: 6 8 10)  \n"
# new_ys = ['6 + 10 = 16 (left: 5 13 16)  \n13 + 16 = 29 (left: 5 29)  \n29 - 5 = 24 (left: 24)\nSteps:  \n', '6 + 10 = 16 (left: 5 13 16)  \n13 + 16 = 29 (left: 5 29)  \n29 - 5 = 24 (left: 24)\n6 + 10 = 16 (left: 5 13 16)  \n', '6 + 10 = 16 (left: 5 13 16)  \n13 + 16 = 29 (left: 5 29)  \n29 - 5 = 24 (left: 24)\n13 + 16 = 29 (left: 5 29)  \n', '6 + 10 = 16 (left: 5 13 16)  \n13 + 16 = 29 (left: 5 29)  \n29 - 5 = 24 (left: 24)\n29 - 5 = 24 (left: 24)  \n', '6 + 10 = 16 (left: 5 13 16)  \n13 + 16 = 29 (left: 5 29)  \n29 - 5 = 24 (left: 24)\nAnswer: (13 + (6 + 10)) - 5 = 24\n', '6 + 10 = 16 (left: 5 13 16)  \n16 - 5 = 11 (left: 13 11)  \n13 + 11 = 24 (left: 24)\nSteps:  \n', '6 + 10 = 16 (left: 5 13 16)  \n16 - 5 = 11 (left: 13 11)  \n13 + 11 = 24 (left: 24)\n6 + 10 = 16 (left: 5 13 16)  \n', '6 + 10 = 16 (left: 5 13 16)  \n16 - 5 = 11 (left: 13 11)  \n13 + 11 = 24 (left: 24)\n16 - 5 = 11 (left: 13 11)  \n', '6 + 10 = 16 (left: 5 13 16)  \n16 - 5 = 11 (left: 13 11)  \n13 + 11 = 24 (left: 24)\n13 + 11 = 24 (left: 24)  \n', '6 + 10 = 16 (left: 5 13 16)  \n16 - 5 = 11 (left: 13 11)  \n13 + 11 = 24 (left: 24)\nAnswer: (13 + (6 + 10 - 5)) = 24\n', '6 + 10 = 16 (left: 5 13 16)  \n16 - 5 = 11 (left: 13 11)  \n13 + 11 = 24 (left: 24)\n\n', '6 + 10 = 16 (left: 5 13 16)  \n16 - 5 = 11 (left: 13 11)  \n13 + 11 = 24 (left: 24)\n---\n', '6 + 10 = 16 (left: 5 13 16)  \n16 - 5 = 11 (left: 13 11)  \n13 + 11 = 24 (left: 24)\n\n', '6 + 10 = 16 (left: 5 13 16)  \n16 - 5 = 11 (left: 13 11)  \n13 + 11 = 24 (left: 24)\nIf you want me to find another way or a different solution, just let me know!\n', '6 + 10 = 16 (left: 5 13 16)  \n16 - 5 = 11 (left: 13 11)  \n11 + 13 = 24 (left: 24)\nYour last example:\n', '6 + 10 = 16 (left: 5 13 16)  \n16 - 5 = 11 (left: 13 11)  \n11 + 13 = 24 (left: 24)\nSteps:  \n', '6 + 10 = 16 (left: 5 13 16)  \n16 - 5 = 11 (left: 13 11)  \n11 + 13 = 24 (left: 24)\n6 + 10 = 16 (left: 5 13 16)  \n', '6 + 10 = 16 (left: 5 13 16)  \n16 - 5 = 11 (left: 13 11)  \n11 + 13 = 24 (left: 24)\n16 - 5 = 11 (left: 13 11)  \n', '6 + 10 = 16 (left: 5 13 16)  \n16 - 5 = 11 (left: 13 11)  \n11 + 13 = 24 (left: 24)\n11 + 13 = 24 (left: 24)  \n', '6 + 10 = 16 (left: 5 13 16)  \n16 - 5 = 11 (left: 13 11)  \n11 + 13 = 24 (left: 24)\n\n', '6 + 10 = 16 (left: 5 13 16)  \n16 - 5 = 11 (left: 13 11)  \n11 + 13 = 24 (left: 24)\nThe final answer is: (6 + 10 - 5) + 13 = 24\n', '6 + 10 = 16 (left: 5 13 16)  \n16 - 5 = 11 (left: 13 11)  \n11 + 13 = 24 (left: 24)\n\n', '6 + 10 = 16 (left: 5 13 16)  \n16 - 5 = 11 (left: 13 11)  \n11 + 13 = 24 (left: 24)\nThis is correct, but since the instructions say "Use numbers and basic arithmetic operations (+ - * /) to obtain 24. Each step, you are only allowed to choose two of the remaining numbers to obtain a new number," this is valid.\n', '6 + 10 = 16 (left: 5 13 16)  \n16 - 5 = 11 (left: 13 11)  \n11 + 13 = 24 (left: 24)\n\n', '6 + 10 = 16 (left: 5 13 16)  \n16 - 5 = 11 (left: 13 11)  \n11 + 13 = 24 (left: 24)\nIf you want, I can provide an alternative solution or confirm this is the final answer.\n', '6 + 10 = 16 (left: 5 13 16)  \n13 - 5 = 8 (left: 16 8)  \n16 + 8 = 24 (left: 24)  \nSteps:  \n', '6 + 10 = 16 (left: 5 13 16)  \n13 - 5 = 8 (left: 16 8)  \n16 + 8 = 24 (left: 24)  \n6 + 10 = 16 (left: 5 13 16)  \n', '6 + 10 = 16 (left: 5 13 16)  \n13 - 5 = 8 (left: 16 8)  \n16 + 8 = 24 (left: 24)  \n13 - 5 = 8 (left: 16 8)  \n', '6 + 10 = 16 (left: 5 13 16)  \n13 - 5 = 8 (left: 16 8)  \n16 + 8 = 24 (left: 24)  \n16 + 8 = 24 (left: 24)  \n', '6 + 10 = 16 (left: 5 13 16)  \n13 - 5 = 8 (left: 16 8)  \n16 + 8 = 24 (left: 24)  \nAnswer: (6 + 10) + (13 - 5) = 24\n', '6 + 10 = 16 (left: 5 13 16)  \n13 - 5 = 8 (left: 16 8)  \n8 + 16 = 24 (left: 24)  \nSteps:  \n', '6 + 10 = 16 (left: 5 13 16)  \n13 - 5 = 8 (left: 16 8)  \n8 + 16 = 24 (left: 24)  \n6 + 10 = 16 (left: 5 13 16)  \n', '6 + 10 = 16 (left: 5 13 16)  \n13 - 5 = 8 (left: 16 8)  \n8 + 16 = 24 (left: 24)  \n13 - 5 = 8 (left: 16 8)  \n', '6 + 10 = 16 (left: 5 13 16)  \n13 - 5 = 8 (left: 16 8)  \n8 + 16 = 24 (left: 24)  \n8 + 16 = 24 (left: 24)  \n', '6 + 10 = 16 (left: 5 13 16)  \n13 - 5 = 8 (left: 16 8)  \n8 + 16 = 24 (left: 24)  \nAnswer: (6 + 10) + (13 - 5) = 24\n']
task = Game24Task()
start = time.perf_counter()
# global gpt
# gpt = partial(gpt, model="gpt-4", temperature=0.7)
for i in range(5):
    print(x)
    # value_outputs = gpt(value_prompt, model="gpt-4.1-mini", n=1, stop=None, max_tokens=200)
    # proposals = [s for s in value_outputs if not ("Input" in s or "steps" in s)]
    # value = task.value_outputs_unwrap(x, y, value_outputs)
    values = get_values(task, x, new_ys, 3)
    print(values)
    # print(proposals)
    # .split('\n')
    # proposals = [s for s in proposals if not ("Input" in s or "steps" in s)]
    # value = get_value(Game24Task(), x, y, 1, cache_value = False)
elapsed = time.perf_counter() - start
print(f"{elapsed:.6f} seconds")
# print(value)