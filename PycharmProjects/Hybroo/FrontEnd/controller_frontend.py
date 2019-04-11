from BackEnd.FunctionProblem import FUNCTION
from BackEnd import controller_backend
from flask import Flask, render_template, request, redirect, url_for, flash
from threading import Thread
from numpy import percentile
import statistics
import os
import ast
from werkzeug.serving import run_simple


function_selected_object = None
function_mode = None
function_info = []
to_reload = False


def get_app():
    app = Flask(__name__)
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
    app.debug = True

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/functions')
    def functions():
        function_names = []
        with open(os.path.dirname(__file__) + "/" + os.pardir + "/BackEnd/FunctionProblem/Functions/functions.txt") as f:
            while True:
                line = f.readline()
                if line == "":
                    break
                function_names.append(line.split(';')[0])
        return render_template('1_functions.html', function_names=function_names)

    @app.route('/calling_function')
    def calling_function():
        try:
            function_selected = request.args.get('function_selected')
        except KeyError:
            flash('A function must be selected!')
            return redirect(url_for('.functions'))
        return redirect(url_for('.function_details', function_selected=function_selected))

    @app.route('/function_details')
    def function_details():
        function_selected = request.args.get('function_selected')
        function_selected_object = None
        with open(os.path.dirname(__file__) + "/" + os.pardir + "/BackEnd/FunctionProblem/Functions/functions.txt") as f:
            while True:
                line = f.readline()
                if line == "":
                    break
                if line.startswith(function_selected):
                    function_selected_object = FUNCTION.Function()
                    function_selected_object.build_function(line)
        function_info = [function_selected_object.name, function_selected_object.expr_original, function_selected_object.dimensions, function_selected_object.domain, function_selected_object.location, function_selected_object.best, function_selected_object.constants, function_selected_object.descriptions, function_selected_object.get_format_expression()]
        return render_template('2_function_detail.html', function_info=function_info)

    @app.route('/function_methods')
    def function_methods():
        try:
            dimensions = int(request.args.get('dimensions'))
            return render_template('3_function_methods.html', function_latex=request.args['function_latex'], dimensions=dimensions, function_name=request.args['function_name'])
        except ValueError:
            flash('The dimensions of function must be informed!')
            return redirect(url_for('.functions'))
        except KeyError:
            pass

    @app.route('/function_results')
    def function_results():
        args = {}
        for key in request.args:
            args[key] = request.args.get(key)
            print(key, args[key])

        if not controller_backend.validate_parameters_function(args):
            flash('Every value must be informed!')
            return redirect(url_for('.functions'))

        function_selected_object, function_info = None, None

        with open(os.path.dirname(__file__) + "/" + os.pardir + "/BackEnd/FunctionProblem/Functions/functions.txt") as f:
            while True:
                line = f.readline()
                if line == "":
                    break
                if line.startswith(args['function_name']):
                    try:
                        function_selected_object = FUNCTION.Function()
                        function_selected_object.build_function(line)
                        function_selected_object.set_n_dimension(args['dimensions'])
                        function_info = [function_selected_object.name, function_selected_object.expr_original, function_selected_object.dimensions, function_selected_object.domain, function_selected_object.location, function_selected_object.best, function_selected_object.constants, function_selected_object.descriptions, function_selected_object.get_format_expression()]
                    except Exception:
                        flash('Every value must be informed!')
                        return redirect(url_for('.functions'))

        if args['submit_button'] == 'Execute Once':
            try:
                type_method, methods, times, real_values, func_value = controller_backend.controller_execute_function(function_selected_object)
            except Exception as e:
                flash('Error in proceedings the system was restarted!'+str(e))
                return redirect(url_for('.reload'))
            return render_template('4_function_results.html', function_info=function_info, type_method=type_method, methods=methods, times=times, real_values=real_values,
                                   func_value=func_value)
        else:
            Thread(target=controller_backend.controller_simulate_function_method, args=[function_selected_object]).start()
            return redirect(url_for('.simulation_functions'))

    @app.route('/simulation_functions')
    def simulation_functions():
        with open(os.path.dirname(__file__) + "//static//files//simulation-status.txt") as f:
            text, times, values = [], [], []
            minimum, first_quartile, median, third_quartile, maximum, mean, std = None, None, None, None, None, None, None
            while True:
                line = f.readline()
                (var, _, val) = line.partition(":")
                var = var.strip()
                val = val.strip()
                if var == "":
                    break
                elif var == 'starting':
                    text = "starting"
                    break
                elif var == 'finish':
                    text = "finish"

                    line = f.readline()
                    (var, _, val) = line.partition(":")
                    times = [float(i) for i in val.replace('[', '').replace(']', '').split(',')]

                    line = f.readline()
                    (var, _, val) = line.partition(":")
                    values = [float(i) for i in val.replace('[', '').replace(']', '').split(',')]

                    minimum = [min(times), min(values)]
                    first_quartile = [percentile(times, 25), percentile(values, 25)]
                    median = [percentile(times, 50), percentile(values, 50)]
                    third_quartile = [percentile(times, 75), percentile(values, 75)]
                    maximum = [max(times), max(values)]
                    mean = [statistics.mean(times), statistics.mean(values)]
                    std = [statistics.stdev(times), statistics.stdev(values)]
                    break
                else:
                    text.append([var, val])

        return render_template('5_function_simulation.html', update_time=3, simulation_status=text, times=times, values=values, minimum=minimum, first_quartile=first_quartile,
                               median=median, third_quartile=third_quartile, maximum=maximum, mean=mean, std=std, function_info=function_info)

    @app.route('/instances')
    def instances():
        files = [os.path.basename(x) for x in os.listdir(os.path.dirname(__file__) + "/" + os.pardir + "/BackEnd/InstanceProblem/Instances")]
        vrp, tsp = [], []
        for i in files:
            if i.endswith("vrp"):
                vrp.append(i)
            else:
                tsp.append(i)
        return render_template('instances.html', vrp_names_list=vrp, tsp_names_list=tsp)

    @app.route('/results', methods=['GET'])
    def calling_method():
        args = {}
        for key in request.args:
            args[key] = request.args.get(key)
        if args['submit_button'] == 'Simulation':
            simulation_times = int(args['simulation_times'])

            Thread(target=controller_backend.controller_simulate_method, args=[args, simulation_times]).start()
            # Thread(target=controller_backend.controller_repetition_method, args=[args, simulation_times]).start()
            return redirect(url_for('.simulation', args=args))
        else:
            type_of_method, type_of_problem, instance, method_selected, times, costs = controller_backend.controller_call_method_instance(args)
            instance_info = load_instance_info(instance)
            if type_of_problem == 'tsp':
                return render_template('results_tsp.html', instance_info=instance_info, type_of_method=type_of_method, type_of_problem=type_of_problem, instance=instance,
                                       method_selected=method_selected, times=times, costs=costs)
            else:
                return render_template('results_vrp.html', instance_info=instance_info, type_of_method=type_of_method, type_of_problem=type_of_problem, instance=instance,
                                       method_selected=method_selected, times=times, costs=costs)

    def load_instance_info(name):
        with open(os.path.dirname(__file__) + "//static//files//instances-info.txt") as f:
            while True:
                line = f.readline()
                (var, _, val) = line.partition(":")
                var = var.strip()
                val = val.strip()
                if var == name:
                    return val.split(";")
                elif var == "":
                    break

    @app.route('/simulation')
    def simulation():
        args = ast.literal_eval(request.args['args'])
        type_of_problem = args['type_of_problem']
        if type_of_problem == 'vrp':
            instance = args['instance_selected_vrp']
        else:
            instance = args['instance_selected_tsp']
        method_selected = [args['method_selected_1']]
        type_of_method = args['type_of_method']
        if type_of_method == 'hybrid':
            method_selected.append(args['method_selected_2'])
        instance_info = load_instance_info(instance)

        with open(os.path.dirname(__file__) + "//static//files//simulation-status.txt") as f:
            text, times, costs = [], [], []
            minimum, first_quartile, median, third_quartile, maximum, mean, std = None, None, None, None, None, None, None
            while True:
                line = f.readline()
                (var, _, val) = line.partition(":")
                var = var.strip()
                val = val.strip()
                if var == "":
                    break
                elif var == 'starting':
                    text = "starting"
                    break
                elif var == 'finish':
                    text = "finish"

                    line = f.readline()
                    (var, _, val) = line.partition(":")
                    times = [float(i) for i in val.replace('[', '').replace(']', '').split(',')]

                    line = f.readline()
                    (var, _, val) = line.partition(":")
                    costs = [float(i) for i in val.replace('[', '').replace(']', '').split(',')]

                    minimum = [min(times), min(costs)]
                    first_quartile = [percentile(times, 25), percentile(costs, 25)]
                    median = [percentile(times, 50), percentile(costs, 50)]
                    third_quartile = [percentile(times, 75), percentile(costs, 75)]
                    maximum = [max(times), max(costs)]
                    mean = [statistics.mean(times), statistics.mean(costs)]
                    std = [statistics.stdev(times), statistics.stdev(costs)]
                    break
                else:
                    text.append([var, val])

        return render_template('simulation.html', update_time=1, simulation_status=text, times=times, costs=costs, minimum=minimum, first_quartile=first_quartile, median=median,
                               third_quartile=third_quartile, maximum=maximum, mean=mean, std=std, type_of_problem=type_of_problem, instance_info=instance_info,
                               type_of_method=type_of_method, method_selected=method_selected, instance=instance)

    @app.after_request
    def add_header(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    @app.route('/reload')
    def reload():
        global to_reload
        to_reload = True
        return redirect(url_for('.home'))

    return app


class AppReload(object):
    def __init__(self, create_app):
        self.create_app = create_app
        self.app = create_app()

    def get_application(self):
        global to_reload
        if to_reload:
            self.app = self.create_app()
            to_reload = False
        return self.app

    def __call__(self, environ, start_response):
        app = self.get_application()
        return app(environ, start_response)


def start_system_local():
    application = AppReload(get_app)
    run_simple('127.0.0.1', 5000, application, use_reloader=True, use_debugger=True, use_evalex=True, threaded=True)


def start_system_server(ip):
    application = AppReload(get_app)
    run_simple(ip, 5000, application, use_reloader=True, use_debugger=True, use_evalex=True, threaded=True)
