from random import choice, randint, random
from math import exp, log


class SA(object):
    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self, parameter):
        self.instance_problem = None
        self.current_solution = None
        self.best_solution = None
        self.solution_list = []
        self.iteration = 1

        self.T = parameter[0]
        self.alpha = parameter[1]
        self.stopping_T = parameter[2]
        self.stopping_iter = parameter[3]
        self.hybrid_individual = parameter[4]

    def solve(self, instance):
        self.instance_problem = instance
        self.solution_list.clear()

        if self.hybrid_individual is None:
            self.current_solution = self.initial_solution()
            self.T = log(self.current_solution.fitness)
        else:
            self.current_solution = Solution(self.instance_problem, self.hybrid_individual)

        self.solution_list.append(self.current_solution)
        self.best_solution = self.current_solution

        while self.T >= self.stopping_T and self.iteration < self.stopping_iter:
            candidate_nodes = list(self.current_solution.nodes)
            upper = randint(2, self.instance_problem.dimension - 1)
            lower = randint(0, self.instance_problem.dimension - upper)
            candidate_nodes[lower: (lower + upper)] = reversed(candidate_nodes[lower: (lower + upper)])

            self.accept_candidate(Solution(self.instance_problem, candidate_nodes))
            self.T *= self.alpha
            self.iteration += 1
            self.solution_list.append(self.current_solution)

        fitness_list = [i.fitness for i in self.solution_list]
        return self.best_solution.nodes, self.best_solution.fitness, fitness_list

    def initial_solution(self):
        nodes = list(range(self.instance_problem.dimension))
        cur_node = choice(nodes)
        solution = [cur_node]
        free_nodes = set(nodes)
        free_nodes.remove(cur_node)
        while free_nodes:
            next_node = min(free_nodes, key=lambda x: self.instance_problem.node_distances[cur_node][x])
            free_nodes.remove(next_node)
            solution.append(next_node)
            cur_node = next_node
        return Solution(self.instance_problem, solution)

    def accept_candidate(self, candidate):
        if candidate.fitness < self.current_solution.fitness:
            self.current_solution = candidate
            if candidate.fitness < self.best_solution.fitness:
                self.best_solution = candidate
        else:
            if random() < exp(-abs(candidate.fitness - self.current_solution.fitness) / self.T):
                self.current_solution = candidate


class Solution(object):
    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self, instance, nodes):
        self.nodes = nodes
        self.instance = instance
        self.fitness = instance.compute_tsp_distance(self.nodes)
