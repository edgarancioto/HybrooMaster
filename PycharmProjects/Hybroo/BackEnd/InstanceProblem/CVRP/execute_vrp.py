from BackEnd.InstanceProblem.CVRP import _ACO, _GA, _SA
from BackEnd.InstanceProblem.INSTANCE import Instance
import time


def execute_some_method(problem, method, parameters):
    instance = Instance()
    instance.load_instance(problem)
    x = time.time()
    if method == 'Ant Colony Optimization':
        path, routes, cost, fitness_list = _ACO.ACO(parameters).solve(instance)
    elif method == 'Genetic Algorithm':
        path, routes, cost, fitness_list = _GA.GA(parameters).solve(instance)
    else:
        path, routes, cost, fitness_list = _SA.SA(parameters).solve(instance)
    return [(time.time() - x), path, routes, cost, instance.node_coord, fitness_list]



