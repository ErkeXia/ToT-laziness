import re
import os
import sympy
import pandas as pd
from tot.tasks.base import Task, DATA_PATH
from tot.prompts.game24 import * 


def get_current_numbers(y: str) -> str:
    last_line = y.strip().split('\n')[-1]
    return last_line.split('left: ')[-1].split(')')[0]


class Game24Task(Task):
    """
    Input (x)   : a string of 4 numbers
    Output (y)  : a trajectory of 3 steps to reach 24
    Reward (r)  : 0 or 1, depending on whether the trajectory is correct
    Input Example: 
        1 2 3 4
    Output Example: 
        1 + 2 = 3 (left: 3 3 4)
        3 + 3 = 6 (left: 4 6)
        6 * 4 = 24 (left: 24)
        (1 + 2 + 3) * 4 = 24
    """
    def __init__(self, file='24.csv'):
        """
        file: a csv file (fixed)
        """
        super().__init__()
        path = os.path.join(DATA_PATH, '24', file)
        self.data = list(pd.read_csv(path)['Puzzles'])
        self.value_cache = {}
        self.steps = 4
        self.stops = ['\n'] * 4

    def __len__(self) -> int:
        return len(self.data)
    
    def get_input(self, idx: int) -> str:
        return self.data[idx]

    def test_output(self, idx: int, output: str):
        expression = output.strip().split('\n')[-1].lower().replace('answer: ', '').split('=')[0]
        numbers = re.findall(r'\d+', expression)
        problem_numbers = re.findall(r'\d+', self.data[idx])
        if sorted(numbers) != sorted(problem_numbers):
            return {'r': 0}
        try:
            # print(sympy.simplify(expression))
            return {'r': int(sympy.simplify(expression) == 24)}
        except Exception as e:
            # print(e)
            return {'r': 0}
            
    @staticmethod
    def standard_prompt_wrap(x: str, y:str='') -> str:
        return standard_prompt.format(input=x) + y

    @staticmethod
    def cot_prompt_wrap(x: str, y:str='') -> str:
        return cot_prompt.format(input=x) + y
    
    @staticmethod
    def propose_prompt_wrap(x: str, y: str='') -> str:
        current_numbers = get_current_numbers(y if y else x)
        if current_numbers.strip() == '24':
            prompt = cot_prompt.format(input=x) + 'Steps:' + y
            # print([prompt])
        else:
            # prompt = propose_prompt.format(input=current_numbers)
            prompt = propose_gpt_4_1.format(input=current_numbers)
        return prompt
    
    @staticmethod
    def value_prompt_wrap(x: str, y: str) -> str:
        last_line = y.strip().split('\n')[-1]
        if 'left: ' not in last_line:  # last step
            ans = last_line.lower().replace('answer: ', '')
            # print([value_last_step_prompt.format(input=x, answer=ans)])
            return value_last_step_prompt.format(input=x, answer=ans)
        current_numbers = get_current_numbers(y)
        return value_prompt.format(input=current_numbers)
    
    @staticmethod
    def value_outputs_unwrap(x: str, y: str, value_outputs: list) -> float:
        if len(y.strip().split('\n')) == 4 and 'answer' not in y.lower():
            print(f"y = {y}\n")
            return 0
        value_names = [_.split('\n')[-1] for _ in value_outputs]
        # print(f"value name: {value_names}")
        value_map = {'impossible': 0.001, 'likely': 1, 'sure': 20}  # TODO: ad hoc
        # value = sum(value * value_names.count(name) for name, value in value_map.items())
        value = 0
        for name in value_names:
            for keyword, score in value_map.items():
                if keyword in name:
                    value += score
                    break
        return value
    
    @staticmethod
    def check_answer(number_str, expression):
        numbers = list(map(float, number_str.strip().split()))
        expression = expression.replace(' ', '')
        match = re.fullmatch(r'(.+)=([\d\.]+)', expression)
        if not match:
            return False, "Expression must be of the form '<expr> = 24'"
        expr_part, result_str = match.groups()
        try:
            target_result = float(result_str)
            if abs(target_result - 24) > 1e-6:
                return False, f"Right-hand side is not 24 (got {target_result})"
            used_numbers = list(map(float, re.findall(r'\d+\.?\d*', expr_part)))
            input_numbers = list(map(float, numbers))
            if sorted(used_numbers) != sorted(input_numbers):
                return False, f"Used numbers {used_numbers} do not match input numbers {input_numbers}"
            result = eval(expr_part)
            if abs(result - 24) > 1e-6:
                return False, f"Expression evaluates to {result}, not 24"
            return True, "Correct"
        except Exception as e:
            return False, f"Invalid math operation: {e}"
        
        
    @staticmethod
    def check_multistep_solution(initial_numbers_str: str, steps_str: str):
        try:
            initial_numbers = list(map(float, initial_numbers_str.strip().split()))
        except:
            return False, "Invalid initial numbers format"
        available = initial_numbers[:]
        steps = steps_str.strip().splitlines()
        for i, line in enumerate(steps):
            line = line.strip()
            match = re.fullmatch(r'\s*(.+?)\s*=\s*([\d\.]+)\s*\(left:\s*([\d\s]+)\s*\)', line)
            if not match:
                return False, f"Line {i+1} format invalid: '{line}'"
            expr_str, result_str, left_str = match.groups()
            try:
                expr_match = re.fullmatch(r'(\d+\.?\d*)\s*([\+\-\*/])\s*(\d+\.?\d*)', expr_str.strip())
                if not expr_match:
                    return False, f"Line {i+1} has invalid expression format: '{expr_str.strip()}'"
                a, op, b = expr_match.groups()
                a = float(a)
                b = float(b)
                result = float(result_str)
            except Exception as e:
                return False, f"Line {i+1} expression error: {e}"
            if op == '+':
                expected = a + b
            elif op == '-':
                expected = a - b
            elif op == '*':
                expected = a * b
            elif op == '/':
                if abs(b) < 1e-8:
                    return False, f"Line {i+1}: Division by zero"
                expected = a / b
            else:
                return False, f"Line {i+1}: Unsupported operator '{op}'"
            if abs(expected - result) > 1e-6:
                return False, f"Line {i+1}: {a} {op} {b} = {expected}, not {result}"
            try:
                available.remove(a)
                available.remove(b)
            except ValueError:
                return False, f"Line {i+1}: Tried to use {a} or {b}, which are not in available numbers {available}"
            available.append(result)
            expected_remaining = list(map(float, left_str.strip().split()))
            if sorted(available) != sorted(expected_remaining):
                return False, f"Line {i+1}: Remaining mismatch. Got {sorted(available)}, expected {sorted(expected_remaining)}"
        if len(available) != 1 or abs(available[0] - 24) > 1e-6:
            return False, f"Final result is {available[0]}, not 24"
        return True, "Correct solution"
                