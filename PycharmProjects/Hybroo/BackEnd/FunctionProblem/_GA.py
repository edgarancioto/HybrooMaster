from random import randint, random


class GA(object):
    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self, parameter):
        self.function_problem = None
        self.chromosome_list = []
        self.generation_results = []
        self.fitness_list = []

        self.population_size = parameter[0]
        self.generation = parameter[1]
        self.elite_count = parameter[2]
        self.crossover_rate = parameter[3]
        self.mutation_rate = parameter[4]
        self.hybrid_individual = parameter[5]

    def solve(self, func):
        self.function_problem = func
        self.chromosome_list.clear()
        self.generation_results.clear()
        self.fitness_list.clear()

        if self.hybrid_individual is not None:
            self.chromosome_list.append(Chromosome(self.function_problem, self.hybrid_individual))
            self.generation_results.append(self.chromosome_list[0])

        self.population_create()
        for i in range(self.generation):
            for j in range(int(self.crossover_rate * self.population_size)):
                self.crossover()
            for j in range(int(self.mutation_rate * self.population_size)):
                self.mutation()
            self.elite_survivors()
            self.generation_results.append(self.chromosome_list[0])
            self.fitness_list.append(self.chromosome_list[0].get_func_value())
            self.new_chromosome()
        return self.fitness_list, self.generation_results[-1].bits_values, self.generation_results[-1].real_values, self.generation_results[-1].func_value

    def population_create(self):
        for i in range(self.population_size):
            self.chromosome_list.append(Chromosome(self.function_problem, None))

    def crossover(self):
        aux = self.chromosome_list[randint(0, self.population_size - 1)]
        pai1 = self.chromosome_list[randint(0, self.population_size - 1)]
        if pai1.func_value > aux.func_value:
            pai1 = aux
        aux = self.chromosome_list[randint(0, self.population_size - 1)]
        pai2 = self.chromosome_list[randint(0, self.population_size - 1)]
        if pai2.func_value > aux.func_value:
            pai2 = aux
        aux1 = [0] * self.function_problem.dimensions
        aux2 = [0] * self.function_problem.dimensions
        for j in range(self.function_problem.dimensions):
            aux1[j] = [0] * 64
            aux2[j] = [0] * 64
            r_pos = randint(0, 63)
            for i in range(64):
                if i < r_pos:
                    aux1[j][i] = pai1.bits_values[j][i]
                    aux2[j][i] = pai2.bits_values[j][i]
                else:
                    aux1[j][i] = pai2.bits_values[j][i]
                    aux2[j][i] = pai1.bits_values[j][i]
        self.chromosome_list.append(Chromosome(self.function_problem, aux1))
        self.chromosome_list.append(Chromosome(self.function_problem, aux2))

    def mutation(self):
        r_dimension = randint(0, self.function_problem.dimensions - 1)
        r_chromosome = randint(0, 63)
        mutated = self.chromosome_list[randint(0, 63)]
        mutated.bits_values[r_dimension][r_chromosome] = 1 if mutated.bits_values[r_dimension][r_chromosome] == 0 else 0
        self.chromosome_list.append(mutated)

    def elite_survivors(self):
        self.chromosome_list = sorted(self.chromosome_list, key=Chromosome.get_func_value, reverse=False)
        for i in range(self.elite_count, len(self.chromosome_list)):
            del self.chromosome_list[-1]

    def new_chromosome(self):
        for i in range(self.population_size - self.elite_count):
            self.chromosome_list.append(Chromosome(self.function_problem, None))


class Chromosome(object):
    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self, func, values):
        self.bits_length = 64  # represents the number of digits for generate a chromosome
        self.func = func
        self.bits_values = []  # represents the number of vars to construct a chromosome
        self.real_values = []
        self.func_value = 0

        if values is None:
            self.generate_random_digits()
        else:
            self.bits_values = values

        self.calc_adjusted_value()
        self.func_value = self.func.calculate(self.real_values)

    def generate_random_digits(self):
        for i in range(self.func.dimensions):
            d = []
            for j in range(self.bits_length):
                d.append(1 if random() > 0.5 else 0)
            self.bits_values.append(d)

    def calc_adjusted_value(self):
        for i in range(self.func.dimensions):
            limit_a, limit_b = self.func.get_domain(i)
            self.real_values.append(limit_a + (limit_b - limit_a) * (self.conversion_decimal(self.bits_values[i]) / (2 ** self.bits_length - 1)))

    def conversion_decimal(self, dig):
        v = 0
        for i in range(self.bits_length, 0, -1):
            v += dig[i - 1] * pow(2, self.bits_length - i)
        return v

    def get_func_value(self):
        return self.func_value
