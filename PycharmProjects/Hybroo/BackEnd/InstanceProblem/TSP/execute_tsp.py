from BackEnd.InstanceProblem.TSP import _GA, _ACO, _SA
from BackEnd.InstanceProblem.INSTANCE import Instance
import time


def execute_some_method(problem, method, parameters):
    instance = Instance()
    instance.load_instance(problem)
    x = time.time()
    if method == 'Ant Colony Optimization':
        path, cost, fitness_list = _ACO.ACO(parameters).solve(instance)
    elif method == 'Genetic Algorithm':
        path, cost, fitness_list = _GA.GA(parameters).solve(instance)
    else:
        path, cost, fitness_list = _SA.SA(parameters).solve(instance)
    return [(time.time() - x), path, cost, instance.node_coord, fitness_list]
