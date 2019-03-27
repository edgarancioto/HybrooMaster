from BackEnd.InstanceProblem.CVRP import execute_vrp
from BackEnd.InstanceProblem.TSP import execute_tsp
from BackEnd.FunctionProblem import execute_function
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import os
from sympy.plotting import plot3d
from sympy.plotting.plot import Plot, ContourSeries
import numpy as np


plt.rcParams.update({'font.size': 16})
plt.rcParams.update({'figure.max_open_warning': 0})
fitness_history: []
method_history = ""

# global vars to execute functions
type_method, method_1, method_2 = None, None, None
parameters_1, parameters_2 = [], []
simulation_times = 0

# global vars to simulate vrp
best_cost, second_cost = float('inf'), float('inf')
best_time, best_path, best_routes, best_coord = None, None, None, None
second_time, second_path, second_routes, second_coord = None, None, None, None

# global vars to simulate functions
best_function_value, second_function_value = float('inf'), float('inf')
best_point, second_point = None, None
best_fitness, second_fitness = None, None


def reset_values():
    global type_method, method_1, method_2, parameters_1, parameters_2, simulation_times
    type_method, method_1, method_2 = None, None, None
    parameters_1, parameters_2 = [], []
    simulation_times = 0


def validate_parameters_function(args):
    reset_values()
    global type_method, method_1, method_2, parameters_1, parameters_2, simulation_times
    try:
        method_1 = args['method_selected_1']
        if method_1 == 'Simulated Annealing':
            parameters_1.append(int(args['t_sa']))
            parameters_1.append(float(args['alpha_sa']))
            parameters_1.append(float(args['tolerance_sa']))
            parameters_1.append(int(args['iter_sa']))
        elif method_1 == 'Genetic Algorithm':
            parameters_1.append(int(args['population_ga']))
            parameters_1.append(int(args['generation_ga']))
            parameters_1.append(int(float(args['elitism_ga']) * int(args['population_ga'])))
            parameters_1.append(float(args['crossover_ga']))
            parameters_1.append(float(args['mutation_ga']))
        parameters_1.append(None)

        type_method = args['type_of_method']
        if type_method == 'hybrid':
            method_2 = args['method_selected_2']
            if method_2 == 'Simulated Annealing':
                parameters_2.append(int(args['t_sa']))
                parameters_2.append(float(args['alpha_sa']))
                parameters_2.append(float(args['tolerance_sa']))
                parameters_2.append(int(args['iter_sa']))
            elif method_2 == 'Genetic Algorithm':
                parameters_2.append(int(args['population_ga']))
                parameters_2.append(int(args['generation_ga']))
                parameters_2.append(int(float(args['elitism_ga']) * int(args['population_ga'])))
                parameters_2.append(float(args['crossover_ga']))
                parameters_2.append(float(args['mutation_ga']))
        if args['submit_button'] == 'Simulation':
            simulation_times = int(args['simulation_times'])
    except (KeyError, ValueError):
        type_method, method_1, method_2 = None, None, None
        parameters_1, parameters_2 = [], []
        simulation_times = 0.0
        return False
    return True


def controller_execute_function(function_selected_object):
    plot_function3d(function_selected_object)
    time_1, fitness_list_1, bits_values_1, real_values_1, func_value_1 = execute_function.execute_some_method(function_selected_object, method_1, parameters_1)
    plot_err(fitness_list_1, 1, method_1)
    if type_method == 'hybrid':
        parameters_2.append(bits_values_1)
        time_2, fitness_list_2, _, real_values_2, func_value_2 = execute_function.execute_some_method(function_selected_object, method_2, parameters_2)
        plot_err(fitness_list_2, 2, method_2)
        return type_method, [method_1, method_2], [time_1, time_2], [real_values_1, real_values_2], [func_value_1, func_value_2]
    return type_method, method_1, time_1, real_values_1, func_value_1


def controller_simulate_function_method(function_selected_object):
    times, values = [], []
    update_simulation_function_progress(0, [1], [0])
    plot_function3d(function_selected_object)
    for i in range(simulation_times):
        time_1, fitness_list_1, bits_values_1, real_values_1, func_value_1 = execute_function.execute_some_method(function_selected_object, method_1, parameters_1)
        update_function_bests(func_value_1, time_1, real_values_1, fitness_list_1)
        if type_method == 'hybrid':
            parameters_2.append(bits_values_1)
            time_2, fitness_list_2, _, real_values_2, func_value_2 = execute_function.execute_some_method(function_selected_object, method_2, parameters_2)
            update_function_bests(func_value_2, time_2, real_values_2, fitness_list_1 + fitness_list_2)
            times.append(round(time_1 + time_2, 2))
            values.append(func_value_2)
        else:
            times.append(round(time_1, 2))
            values.append(func_value_1)
        update_simulation_function_progress(i, times, values)
    prepare_results_function_simulation(times, values, method_1, method_2)


# function just for tests in programmer mode
def controller_repetition_function_method(function_selected_object):
    times, fitness_values = [], []

    print("log: Solving the function", function_selected_object.name)
    for i in range(simulation_times):
        print("log: Repetition nº", i)
        time_1, fitness_list_1, bits_values_1, real_values_1, func_value_1 = execute_function.execute_some_method(function_selected_object, method_1, parameters_1)
        if type_method == 'hybrid':
            parameters_2.append(bits_values_1)
            time_2, fitness_list_2, _, real_values_2, func_value_2 = execute_function.execute_some_method(function_selected_object, method_2, parameters_2)
            times.append(round(time_1 + time_2, 2))
            fitness_values.append(fitness_list_2)
        else:
            times.append(round(time_1, 2))
            fitness_values.append(fitness_list_1)
        print("log: Solved function", function_selected_object.name, i, "times")

        file_name = str(method_1)
        if type_method == 'hybrid':
            file_name += "+" + str(method_2)
        file_name += "-" + str(function_selected_object.name)
        save_repetition(file_name, times[-1], fitness_values[-1])


def update_function_bests(function_value, time, point, fitness):
    global best_function_value, second_function_value, best_point, second_point, best_time, second_time, best_fitness, second_fitness
    if function_value < best_function_value:
        second_function_value = best_function_value
        second_time = best_time
        second_point = best_point
        second_fitness = best_fitness
        best_function_value = function_value
        best_time = time
        best_point = point
        best_fitness = fitness
    else:
        if function_value < second_function_value:
            second_function_value = function_value
            second_time = time
            second_point = point
            second_fitness = fitness


def update_simulation_function_progress(count, times, func_values):
    try:
        arq_w = open(os.getcwd() + "/FrontEnd/static/files/simulation-status.txt", "w")
    except FileNotFoundError:
        arq_w = open(os.getcwd() + "/FrontEnd/static/files/simulation-status.txt", "w+")

    if count == 0:
        text = 'starting'
    elif count + 1 == simulation_times:
        text = 'finish'
        text += "\nTimes: " + str(times)
        text += "\nValues: " + str(func_values)
    else:
        text = "Total of simulations: " + str(simulation_times)
        text += "\nExecuted: " + str(count + 1)
        avg = sum(times) / len(times)
        text += "\nAverage Time: " + str(avg)
        text += "\nTime Left: " + str((simulation_times - (count + 1)) * avg)
    arq_w.write(text)
    arq_w.close()


def plot_function3d(function_selected_object):
    if function_selected_object.dimensions == 2:
        plot_3d = plot3d(function_selected_object.expr, ('x', function_selected_object.domain[0][0], function_selected_object.domain[0][1]),
                         ('y', function_selected_object.domain[1][0], function_selected_object.domain[1][1]), show=False)
        plot_contour = Plot(ContourSeries(function_selected_object.expr, ('x', function_selected_object.domain[0][0], function_selected_object.domain[0][1]),
                                          ('y', function_selected_object.domain[1][0], function_selected_object.domain[1][1])))
        try:
            plot_3d.save(os.getcwd() + "/FrontEnd/static/image/results/function3d")
            plot_contour.save(os.getcwd() + "/FrontEnd/static/image/results/function_contour")
        except ZeroDivisionError:
            remove_fig('function3d.png')
            remove_fig('function_contour.png')
    else:
        x = list(range(-32, 32, 2))
        y = list(range(-32, 32, 2))
        x, y = np.meshgrid(x, y)
        z = []
        for i in range(len(x)):
            for j in range(len(x[i])):
                z.append(function_selected_object.calculate_to_print_n([x[i][j], y[i][j]]))
        x = np.array(x)
        y = np.array(y)
        z = np.array(z)
        z = z.reshape((len(x), len(y)))
        fig = plt.figure(figsize=(6.4, 4.8))
        try:
            fig.gca(projection='3d').plot_surface(x, y, z, cmap=cm.viridis, linewidth=0, antialiased=False)
            save_fig('function3d')
        except:
            remove_fig('function3d.png')
        try:
            fig.gca(projection='3d').contour(x, y, z, cmap=cm.viridis, antialiased=False)
            save_fig('function_contour')
        except:
            remove_fig('function_contour.png')


def plot_err(fitness_list, order, method, name_additional=None):
    global fitness_history, method_history
    plt.figure(figsize=(10, 10))
    plt.grid(True)
    plt.ylabel('Solution Cost')
    plt.xlabel('Iterations')

    if name_additional is None:
        name_additional = ''
    if order == 2:
        plt.plot(fitness_list, linestyle='--', color='blue', label=method, linewidth=3)
        save_fig("err_2" + name_additional)
        plt.plot(fitness_history + fitness_list, linestyle='--', color='blue', label=method, linewidth=3)
        plt.plot(fitness_history, linestyle='--', color='orange', label=method_history, linewidth=3)

        if fitness_list[-1] < fitness_history[-1]:
            plt.annotate('%.3f' % fitness_list[-1], (len(fitness_history + fitness_list), fitness_list[-1]), xytext=(-100, 90), textcoords='offset points',
                         bbox=dict(boxstyle="round", fc="0.8"), arrowprops=dict(arrowstyle="->", connectionstyle="angle,angleA=0,angleB=90,rad=10"))
        else:
            plt.annotate('%.3f' % fitness_history[-1], (len(fitness_history), fitness_history[-1]), xytext=(-100, 90), textcoords='offset points',
                         bbox=dict(boxstyle="round", fc="0.8"), arrowprops=dict(arrowstyle="->", connectionstyle="angle,angleA=0,angleB=135,rad=10"))

        plt.legend()
        plt.grid(True)
        save_fig("result_err_hybrid" + name_additional)
    else:
        fitness_history = fitness_list
        method_history = method
        plt.plot(fitness_history, linestyle='--', color='orange', label=method, linewidth=3)
        save_fig("err_1" + name_additional)


def save_fig(name):
    plt.savefig(os.getcwd() + "/FrontEnd/static/image/results/" + name)
    plt.clf()


def remove_fig(name):
    try:
        os.remove(os.getcwd() + "/FrontEnd/static/image/results/" + name)
    except FileNotFoundError:
        pass


def prepare_results_function_simulation(times, values, method_selected_1, method_selected_2=None):
    plt.boxplot(times, labels=['Time(s)'])
    plt.gca().yaxis.grid(True)
    save_fig("times-boxplot")

    plt.boxplot(values, labels=['Values'])
    plt.annotate('%.2f' % min(values), (1, min(values)), xytext=(40, 0), textcoords='offset points', bbox=dict(boxstyle="round", fc="0.8"),
                 arrowprops=dict(arrowstyle="->", connectionstyle="angle,angleA=90,angleB=0,rad=10"))
    plt.gca().yaxis.grid(True)
    save_fig("values-boxplot")

    plt.figure(figsize=(6.4, 5.4))
    plt.scatter(times, values)
    plt.xlabel('Time(s)')
    plt.ylabel('Values')
    save_fig("scatter")

    global best_function_value, best_time, best_point, best_fitness, second_function_value, second_time, second_point, second_fitness

    if method_selected_2 is not None:
        method = method_selected_1+method_selected_2
    else:
        method = method_selected_1
    plot_err(best_fitness, 1, method, '-simulation-1')
    plot_err(second_fitness, 1, method, '-simulation-2')


# ---------------methods of control operations of instances---------------

def controller_call_method_instance(args):
    type_of_method = args['type_of_method']
    type_of_problem, instance, method_selected, parameters = take_parameters_instance(1, args)

    if type_of_problem == 'vrp':
        time, path, routes, cost, coordinates, fitness_list = execute_vrp.execute_some_method(instance, method_selected, parameters)
        prepare_results_vrp(1, method_selected, path, routes, coordinates, fitness_list)

        if type_of_method == 'hybrid':
            _, _, method_selected2, parameters = take_parameters_instance(2, args, path)
            time2, path2, routes2, cost2, _, fitness_list = execute_vrp.execute_some_method(instance, method_selected2, parameters)
            prepare_results_vrp(2, method_selected2, path2, routes2, coordinates, fitness_list)
            return type_of_method, type_of_problem, instance, [method_selected, method_selected2], [time, time2], [cost, cost2]

        return type_of_method, type_of_problem, instance, method_selected, time, cost

    else:
        time, path, cost, coordinates, fitness_list = execute_tsp.execute_some_method(instance, method_selected, parameters)
        prepare_results_tsp(1, method_selected, path, coordinates, fitness_list)

        if type_of_method == 'hybrid':
            _, _, method_selected2, parameters = take_parameters_instance(2, args, path)
            time2, path2, cost2, _, fitness_list = execute_tsp.execute_some_method(instance, method_selected2, parameters)
            prepare_results_tsp(2, method_selected2, path2, coordinates, fitness_list)
            return type_of_method, type_of_problem, instance, [method_selected, method_selected2], [time, time2], [cost, cost2]

        return type_of_method, type_of_problem, instance, method_selected, time, cost


def controller_simulate_method(args, simulation_times):
    times, costs = [], []
    method_selected_2, parameters_2 = None, None
    type_of_method = args['type_of_method']

    type_of_problem, instance, method_selected_1, parameters_1 = take_parameters_instance(1, args)
    if type_of_method == 'hybrid':
        _, _, method_selected_2, parameters_2 = take_parameters_instance(2, args)

    update_simulation_progress(0, simulation_times, [1], [0])

    for i in range(simulation_times):
        if type_of_problem == 'vrp':
            time, path, routes, cost, coordinates, _ = execute_vrp.execute_some_method(instance, method_selected_1, parameters_1)
            update_bests(type_of_problem, cost, time, path, coordinates, routes)
        else:
            time, path, cost, coordinates, _ = execute_tsp.execute_some_method(instance, method_selected_1, parameters_1)
            update_bests(type_of_problem, cost, time, path, coordinates)
        if type_of_method == 'hybrid':
            parameters_2[-1] = path
            if type_of_problem == 'vrp':
                time2, path, routes, cost2, _, _ = execute_vrp.execute_some_method(instance, method_selected_2, parameters_2)
                update_bests(type_of_problem, cost2, time2, path, coordinates, routes)
            else:
                time2, path, cost2, _, _ = execute_tsp.execute_some_method(instance, method_selected_2, parameters_2)
                update_bests(type_of_problem, cost2, time2, path, coordinates)

            times.append(round(time + time2, 2))
            costs.append(cost2)
        else:
            times.append(round(time, 2))
            costs.append(cost)
        update_simulation_progress(i, simulation_times, times, costs)

    prepare_results_simulation(type_of_problem, times, costs)


# function just for tests in programmer mode
def controller_repetition_method(args, simulation_times):
    times, fitness_values = [], []
    method_selected_2, parameters_2 = None, None
    type_of_method = args['type_of_method']

    type_of_problem, instance, method_selected_1, parameters_1 = take_parameters_instance(1, args)
    if type_of_method == 'hybrid':
        _, _, method_selected_2, parameters_2 = take_parameters_instance(2, args)

    print("log: Solving the instance", instance, " by methods ", method_selected_1, method_selected_2)
    for i in range(simulation_times):
        if type_of_problem == 'vrp':
            time, path, _, _, _, fitness_list_1 = execute_vrp.execute_some_method(instance, method_selected_1, parameters_1)
        else:
            time, path, _, _, fitness_list_1 = execute_tsp.execute_some_method(instance, method_selected_1, parameters_1)
        if type_of_method == 'hybrid':
            parameters_2[-1] = path
            if type_of_problem == 'vrp':
                time2, _, _, _, _, fitness_list_2 = execute_vrp.execute_some_method(instance, method_selected_2, parameters_2)
            else:
                time2, _, _, _, fitness_list_2 = execute_tsp.execute_some_method(instance, method_selected_2, parameters_2)
            times.append(round(time + time2, 2))
            fitness_values.append(fitness_list_2)
        else:
            times.append(round(time, 2))
            fitness_values.append(fitness_list_1)
        print("log: Solved instance", instance, i, "times")

        file_name = str(method_selected_1)
        if type_of_method == 'hybrid':
            file_name += "+" + str(method_selected_2)
        file_name += "-" + str(instance)
        save_repetition(file_name, times[-1], fitness_values[-1])


def save_repetition(file_name, time, fitness_list):
    file = os.path.dirname(__file__) + "/TestFiles/" + file_name + ".txt"
    try:
        arq_r = open(file, "r")
        text = arq_r.read()
        arq_w = open(file, "w")
        print("log: file exist")
    except FileNotFoundError:
        arq_w = open(file, "w+")
        text = ""
        print("log: creating a new file")

    text += str(time) + "\t" + str(fitness_list) + "\n"
    arq_w.write(text)
    arq_w.close()
    print("log: file saved")


def update_bests(type_of_problem, cost, time, path, coord, routes=None):
    global best_cost, best_time, best_path, best_coord, best_routes, second_cost, second_time, second_path, second_routes, second_coord
    if cost < best_cost:
        second_cost = best_cost
        best_cost = cost
        second_time = best_time
        best_time = time
        second_path = best_path
        best_path = path
        second_coord = best_coord
        best_coord = coord
        if type_of_problem == 'vrp':
            second_routes = best_routes
            best_routes = routes
    else:
        if cost < second_cost:
            second_cost = cost
            second_time = time
            second_path = path
            second_coord = coord
            if type_of_problem == 'vrp':
                second_routes = routes


def update_simulation_progress(count, simulation_times, times, costs):
    try:
        arq_w = open(os.getcwd() + "/FrontEnd/static/files/simulation-status.txt", "w")
    except FileNotFoundError:
        arq_w = open(os.getcwd() + "/FrontEnd/static/files/simulation-status.txt", "w+")

    if count == 0:
        text = 'starting'
    elif count + 1 == simulation_times:
        text = 'finish'
        text += "\nTimes: " + str(times)
        text += "\nCosts: " + str(costs)
    else:
        text = "Total of simulations: "+str(simulation_times)
        text += "\nExecuted: " + str(count + 1)
        avg = sum(times)/len(times)
        text += "\nAverage Time: " + str(avg)
        text += "\nTime Left: " + str((simulation_times - (count + 1)) * avg)
    arq_w.write(text)
    arq_w.close()


def prepare_results_simulation(type_of_problem, times, costs):
    plt.boxplot(times, labels=['Time(s)'])
    plt.gca().yaxis.grid(True)
    save_fig("times-boxplot")

    plt.boxplot(costs, labels=['Cost'])
    plt.annotate('%.2f' % min(costs), (1, min(costs)), xytext=(40, 0), textcoords='offset points', bbox=dict(boxstyle="round", fc="0.8"),
                 arrowprops=dict(arrowstyle="->", connectionstyle="angle,angleA=90,angleB=0,rad=10"))
    plt.gca().yaxis.grid(True)
    save_fig("costs-boxplot")

    plt.figure(figsize=(6.4, 5.4))
    plt.scatter(times, costs)
    plt.xlabel('Time(s)')
    plt.ylabel('Cost')
    save_fig("scatter")

    global best_cost, best_time, best_path, best_coord, best_routes, second_cost, second_time, second_path, second_routes, second_coord

    title_1 = 'Solved in: '+str(round(best_time, 2))+'(s) with the cost: '+str(round(best_cost, 2))
    title_2 = 'Solved in: ' + str(round(second_time, 2)) + '(s) with the cost: ' + str(round(second_cost, 2))

    if type_of_problem == 'vrp':
        plot_vrp_routs(best_routes, best_coord, best_path, '-best', title_1)
        plot_vrp_routs(second_routes, second_coord, second_path, '-second', title_2)
    else:
        plot_tsp_path(best_coord, best_path, '-best', title_1)
        plot_tsp_path(second_coord, second_path, '-second', title_2)


def prepare_results_tsp(order, method, path, coord, fitness_list):
    plot_tsp_path(coord, path, order)
    plot_err(fitness_list, order, method)


def prepare_results_vrp(order, method, path, routes, coord, fitness_list):
    plot_vrp_routs(routes, coord, path, order)
    plot_err(fitness_list, order, method)


def plot_tsp_path(coord, path, order, title=None):
    plt.clf()
    plt.figure(figsize=(6.4, 4.8))
    x = []
    y = []
    x1 = []
    x2 = []
    for i in range(len(coord)):
        x.append(coord[i][0])
        y.append(coord[i][1])
        x1.append(coord[path[i]][0])
        x2.append(coord[path[i]][1])
    x1.append(x1[0])
    x2.append(x2[0])
    plt.plot(x1, x2, 'co')
    plt.plot(x1, x2)
    plt.axis('off')
    if title is not None:
        plt.title(title)
    save_fig("path" + str(order))


def plot_vrp_routs(routes, coord, path, order, title=None):
    plt.clf()
    plt.figure(figsize=(6.4, 4.8))
    x = []
    y = []
    starts = 0
    for i in routes:
        for j in range(starts, (starts + i)):
            x.append(coord[path[j]][0])
            y.append(coord[path[j]][1])
            plt.text(x[-1], y[-1], str(path[j]))
        starts += i
    starts = 0
    for i in range(len(routes)):
        x1 = [coord[0][0]] + x[starts:starts + routes[i]] + [coord[0][0]]
        y1 = [coord[0][1]] + y[starts:starts + routes[i]] + [coord[0][1]]
        plt.plot(x1, y1)
        starts += routes[i]
    x.append(coord[0][0])
    y.append(coord[0][1])
    plt.plot(x, y, 'co')
    plt.axis('off')
    if title is not None:
        plt.suptitle(title)
    save_fig("route" + str(order))


def take_parameters_instance(order, args, hybrid_parameter=None):
    type_of_problem = args['type_of_problem']
    if type_of_problem == 'vrp':
        instance = args['instance_selected_vrp']
    else:
        instance = args['instance_selected_tsp']

    if order == 1:
        method_selected = args['method_selected_1']
    else:
        method_selected = args['method_selected_2']

    parameters = []
    if method_selected == 'Ant Colony Optimization':
        parameters.append(int(args['ants_aco']))
        parameters.append(int(args['generation_aco']))
        parameters.append(float(args['alpha_aco']))
        parameters.append(int(args['beta_aco']))
        parameters.append(float(args['rho_aco']))
        parameters.append(int(args['q_aco']))
    elif method_selected == 'Simulated Annealing':
        parameters.append(int(args['t_sa']))
        parameters.append(float(args['alpha_sa']))
        parameters.append(float(args['tolerance_sa']))
        parameters.append(int(args['iter_sa']))
        if hybrid_parameter is not None:
            parameters.append(hybrid_parameter)
        else:
            parameters.append(None)
    elif method_selected == 'Genetic Algorithm':
        if type_of_problem == 'vrp':
            parameters.append(int(args['population_ga_vrp']))
            parameters.append(int(args['generation_ga_vrp']))
            parameters.append(int(float(args['elitism_ga_vrp'])*int(args['population_ga_vrp'])))
            parameters.append(float(args['inverse_mutation_ga_vrp']))
            try:
                parameters.append(args['special_individual_ga_vrp'] is not None)
            except KeyError:
                parameters.append(False)
        else:
            parameters.append(int(args['population_ga_tsp']))
            parameters.append(int(args['generation_ga_tsp']))
            parameters.append(int(float(args['elitism_ga_tsp']) * int(args['population_ga_tsp'])))
            parameters.append(float(args['crossover_ga_tsp']))
            parameters.append(float(args['simple_mutation_ga_tsp']))
            parameters.append(float(args['inverse_mutation_ga_tsp']))

            try:
                parameters.append(args['special_individual_ga_tsp'] is not None)
            except KeyError:
                parameters.append(False)
        if hybrid_parameter is not None:
            parameters.append(hybrid_parameter)
        else:
            parameters.append(None)
    return type_of_problem, instance, method_selected, parameters
