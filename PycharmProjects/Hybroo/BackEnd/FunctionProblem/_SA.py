from random import choice, randint, random
from math import exp, log


class SA(object):
    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self, parameter):
        self.function_problem = None
        self.current_solution = None
        self.best_solution = None
        self.bits_length = 64
        self.solution_list = []
        self.iteration = 1

        self.T = parameter[0]
        self.alpha = parameter[1]
        self.stopping_T = parameter[2]
        self.stopping_iter = parameter[3]
        self.hybrid_individual = parameter[4]

    def solve(self, func):
        self.function_problem = func
        self.solution_list.clear()

        if self.hybrid_individual is None:
            self.current_solution = self.random_initial_solution()
        else:
            self.current_solution = Solution(self.function_problem, self.hybrid_individual)
            #self.T = log(self.current_solution.func_value)

        self.solution_list.append(self.current_solution)
        self.best_solution = self.current_solution

        while self.T >= self.stopping_T and self.iteration < self.stopping_iter:
            bits = []
            for i in range(self.function_problem.dimensions):
                candidate_bits = list(self.current_solution.bits_values[i])
                upper = randint(2, self.bits_length - 1)
                lower = randint(0, self.bits_length - upper)
                candidate_bits[lower: (lower + upper)] = reversed(candidate_bits[lower: (lower + upper)])
                bits.append(candidate_bits)
            self.accept_candidate(Solution(self.function_problem, bits))
            self.T *= self.alpha
            self.iteration += 1
            self.solution_list.append(self.current_solution)

        fitness_list = [i.func_value for i in self.solution_list]
        return fitness_list, self.best_solution.bits_values, self.best_solution.real_values, self.best_solution.func_value

    def random_initial_solution(self):
        bits = []
        for i in range(self.function_problem.dimensions):
            d = []
            for j in range(self.bits_length):
                d.append(1 if random() > 0.5 else 0)
            bits.append(d)
        return Solution(self.function_problem, bits)

    def accept_candidate(self, candidate):
        if candidate.func_value < self.current_solution.func_value:
            self.current_solution = candidate
            if candidate.func_value < self.best_solution.func_value:
                self.best_solution = candidate
        else:
            if random() < exp(-abs(candidate.func_value - self.current_solution.func_value) / self.T):
                self.current_solution = candidate


class Solution(object):
    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self, func, values):
        self.bits_length = 64  # represents the number of digits for generate a chromosome
        self.func = func
        self.bits_values = values  # represents the number of vars to construct a chromosome
        self.real_values = []

        self.calc_adjusted_value()
        self.func_value = self.func.calculate(self.real_values)

    def calc_adjusted_value(self):
        for i in range(self.func.dimensions):
            limit_a, limit_b = self.func.get_domain(i)
            try:
                self.real_values.append(limit_a + (limit_b - limit_a) * (self.conversion_decimal(self.bits_values[i]) / (2 ** self.bits_length - 1)))
            except Exception as e:
                print(limit_a, limit_b, self.bits_values, e)

    def conversion_decimal(self, dig):
        v = 0
        for i in range(self.bits_length, 0, -1):
            v += dig[i - 1] * pow(2, self.bits_length - i)
        return v
