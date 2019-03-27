import random


class ACO(object):
    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self, parameter):
        self.instance_problem = None
        self.pheromone = []
        self.best_cost = float('inf')
        self.best_solution = []
        self.best_routes = []
        self.fitness_list = []

        self.ant_count = parameter[0]
        self.generations = parameter[1]
        self.alpha = parameter[2]
        self.beta = parameter[3]
        self.rho = parameter[4]
        self.Q = parameter[5]
        self.update_strategy = 2

    def solve(self, instance):
        self.instance_problem = instance
        self.pheromone = [[1 / (self.instance_problem.dimension * self.instance_problem.dimension) for _ in range(self.instance_problem.dimension)] for _ in
                          range(self.instance_problem.dimension)]

        for gen in range(self.generations):
            ants = [Ant(self, self.instance_problem) for _ in range(self.ant_count)]
            for ant in ants:
                for i in range(self.instance_problem.dimension - 1):
                    ant.select_next()
                ant.adjust_real_path()
                ant.routes = self.instance_problem.compute_vrp_routes(ant.real_path)
                ant.total_cost = self.instance_problem.compute_vrp_distance(ant.routes, ant.real_path)
                if ant.total_cost < self.best_cost:
                    self.best_cost = ant.total_cost
                    self.best_solution = [] + ant.real_path
                    self.best_routes = [] + ant.routes
                ant.update_pheromone_delta()
            self.fitness_list.append(self.best_cost)
            self.update_pheromone(ants)
        return self.best_solution, self.best_routes, self.best_cost, self.fitness_list

    def update_pheromone(self, ants):
        for i, row in enumerate(self.pheromone):
            for j, col in enumerate(row):
                self.pheromone[i][j] *= self.rho
                for ant in ants:
                    self.pheromone[i][j] += ant.pheromone_delta[i][j]


class Ant(object):
    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self, aco, instance):
        self.total_cost = 0.0
        self.cities = []
        self.pheromone_delta = []
        self.routes = []
        self.real_path = []

        self.colony = aco
        self.instance = instance

        self.allowed = [i for i in range(self.instance.dimension)]
        self.eta = [[0 if (i == j or self.instance.node_distances[i][j] == 0) else 1 / self.instance.node_distances[i][j] for j in range(self.instance.dimension)] for i in
                    range(self.instance.dimension)]
        self.current = random.randint(0, self.instance.dimension - 1)
        self.cities.append(self.current)
        self.allowed.remove(self.current)

    def select_next(self):
        denominator = 0.0
        selected = 0

        for i in self.allowed:
            denominator += self.colony.pheromone[self.current][i] ** self.colony.alpha * self.eta[self.current][i] ** self.colony.beta

        probabilities = [0 for _ in range(self.instance.dimension)]
        for i in range(self.instance.dimension):
            try:
                self.allowed.index(i)
                probabilities[i] = self.colony.pheromone[self.current][i] ** self.colony.alpha * self.eta[self.current][i] ** self.colony.beta / denominator
            except ValueError:
                pass
            except ZeroDivisionError:
                selected = self.allowed[0]

        rand = random.random()
        for i, probability in enumerate(probabilities):
            rand -= probability
            if rand <= 0:
                selected = i
                break

        self.allowed.remove(selected)
        self.cities.append(selected)
        self.total_cost += self.instance.node_distances[self.current][selected]
        self.current = selected

    def adjust_real_path(self):
        self.real_path = self.cities.copy()
        self.real_path.remove(0)

    def update_pheromone_delta(self):
        self.pheromone_delta = [[0 for _ in range(self.instance.dimension)] for _ in range(self.instance.dimension)]
        for _ in range(1, len(self.cities)):
            i = self.cities[_ - 1]
            j = self.cities[_]
            if self.colony.update_strategy == 1:
                self.pheromone_delta[i][j] = self.colony.Q
            elif self.colony.update_strategy == 2:
                try:
                    self.pheromone_delta[i][j] = self.colony.Q / self.instance.node_distances[i][j]
                except ZeroDivisionError:
                    self.pheromone_delta[i][j] = 0
            else:
                self.pheromone_delta[i][j] = self.colony.Q / self.total_cost
