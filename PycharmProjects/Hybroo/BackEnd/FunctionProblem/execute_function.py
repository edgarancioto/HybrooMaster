from BackEnd.FunctionProblem import _GA, _SA
import time


def execute_some_method(function_selected_object, method, parameters):
    x = time.time()
    if method == 'Genetic Algorithm':
        fitness_list, bits_values, real_values, func_value = _GA.GA(parameters).solve(function_selected_object)
    else:
        fitness_list, bits_values, real_values, func_value = _SA.SA(parameters).solve(function_selected_object)
    if function_selected_object.multidimensional:
        del real_values[0]
    return [(time.time() - x), fitness_list, bits_values, real_values, func_value]
