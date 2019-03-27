from random import randint, shuffle, choice


class GA(object):
    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self, parameter):
        self.instance_problem = None
        self.chromosome_list = []
        self.generation_results = []
        self.fitness_list = []

        self.population_size = parameter[0]
        self.generation = parameter[1]
        self.elite_count = parameter[2]
        self.inverse_mutation_rate = parameter[3]
        self.use_special_individual = parameter[4]
        self.hybrid_individual = parameter[5]

    def solve(self, instance):
        self.instance_problem = instance
        self.chromosome_list.clear()
        self.generation_results.clear()
        self.fitness_list.clear()

        if self.hybrid_individual is not None:
            self.chromosome_list.append(Chromosome(self.instance_problem, self.hybrid_individual))
            self.generation_results.append(self.chromosome_list[0])

        if self.use_special_individual:
            self.chromosome_list.append(self.special_individual())

        self.population_create()
        for i in range(self.generation):
            for j in range(int(self.inverse_mutation_rate * self.population_size)):
                self.inverse_mutation()
            self.classification()
            self.local_search()
            self.classification()
            self.generation_results.append(self.chromosome_list[0])
            self.fitness_list.append(self.chromosome_list[0].get_distance())
            self.elite_survivors()
            self.restore_population()
        return self.generation_results[-1].genes_order, self.generation_results[-1].routes_vector, self.generation_results[-1].get_distance(), self.fitness_list

    def population_create(self):
        for i in range(self.population_size):
            self.chromosome_list.append(Chromosome(self.instance_problem, None))

    def special_individual(self):
        nodes = list(range(1, self.instance_problem.dimension))
        cur_node = choice(nodes)
        solution = [cur_node]
        free_nodes = set(nodes)
        free_nodes.remove(cur_node)
        while free_nodes:
            next_node = min(free_nodes, key=lambda x: self.instance_problem.node_distances[cur_node][x])
            free_nodes.remove(next_node)
            solution.append(next_node)
            cur_node = next_node
        return Chromosome(self.instance_problem, solution)

    def inverse_mutation(self):
        flag_insert = False
        block_vector = [0] * 4
        selected = self.chromosome_list[randint(0, self.population_size - 1)]
        copy = selected.genes_order.copy()
        best_value = selected.get_distance()

        for i in range(len(block_vector)):
            block_vector[i] = randint(0, self.instance_problem.dimension - 1)
        block_vector = sorted(block_vector)

        for i in range(0, len(block_vector), 2):
            copy[block_vector[i]: block_vector[i + 1]] = reversed(copy[block_vector[i]: block_vector[i + 1]])
            assistant = Chromosome(self.instance_problem, copy.copy())

            if assistant.get_distance() < best_value:
                self.chromosome_list.append(assistant)
                best_value = assistant.get_distance()
                flag_insert = True
        if not flag_insert:
            self.chromosome_list.append(Chromosome(self.instance_problem, copy))

    def classification(self):
        self.chromosome_list = sorted(self.chromosome_list, key=Chromosome.get_distance)

    def local_search(self):
        best = self.chromosome_list[0]
        copy = best.genes_order.copy()
        for i in range(self.instance_problem.dimension-2):
            x = copy[i]
            copy[i] = copy[i+1]
            copy[i+1] = x
            assistant = Chromosome(self.instance_problem, copy)
            if assistant.get_distance() < best.get_distance():
                self.chromosome_list.append(assistant)

    def elite_survivors(self):
        for i in range(self.elite_count, len(self.chromosome_list)):
            del self.chromosome_list[-1]

    def restore_population(self):
        for i in range(self.population_size - self.elite_count):
            self.chromosome_list.append(Chromosome(self.instance_problem, None))


class Chromosome(object):
    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self, instance, genes):
        self.instance = instance
        self.routes_vector = []

        if genes is None:
            self.genes_order = list(range(1, self.instance.dimension))
            shuffle(self.genes_order)
        else:
            self.genes_order = genes
        self.routes_vector = instance.compute_vrp_routes(self.genes_order)
        self.distance = instance.compute_vrp_distance(self.routes_vector, self.genes_order)

    def get_distance(self):
        return self.distance
