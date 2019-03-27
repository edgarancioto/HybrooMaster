from sympy import sympify, lambdify, latex, Symbol
import ast


class Function(object):
    def __init__(self):
        self.name = None
        self.expr = None
        self.expr_original = None
        self.dimensions = 0
        self.domain = None
        self.location = None
        self.best = None
        self.constants = None
        self.descriptions = None
        self.multidimensional = False

    def __str__(self):
        return """Name: %s \nFunction : %s \nDimensions: %s \nDomain: %s \nLocation: %s \nBest: %s \nConstants: %s \nDescription: %s \n""" % \
               (self.name, self.expr, self.dimensions, self.domain, self.location, self.best, self.constants, self.descriptions)

    def build_function(self, string):
        self.name, self.descriptions, self.expr, self.constants, self.domain, self.location, self.best = string.replace('\n', '').split(';')
        self.dimensions = self.convert_value(self.descriptions.split(',')[0].split('-')[0])

        self.constants = ast.literal_eval(self.constants)
        if self.constants is not None:
            for i in self.constants:
                self.constants[i] = self.convert_value(self.constants[i])

        self.best = self.convert_value(self.best)
        self.domain = self.browse_vector(self.domain, self.dimensions)
        self.location = self.browse_vector(self.location, self.dimensions)

        if self.dimensions == Symbol('n') or self.dimensions > 3:
            self.multidimensional = True
            self.expr = self.expr.replace('x[', "IndexedBase('x')[")

        self.expr = sympify(self.expr, evaluate=False)

        if self.constants is not None:
            for i in self.constants:
                self.expr = self.expr.subs(i, self.constants[i])

        self.expr_original = self.expr.copy()

    @staticmethod
    def browse_vector(vector, dimensions):
        try:
            vector = ast.literal_eval(vector)
        except ValueError:
            vector = sympify(vector)

        values = []
        for i in vector:
            values.append(Function.convert_value(i))
        if type(values[0]) is not list and type(dimensions) is int:
            return [values] * dimensions
        else:
            return values

    @staticmethod
    def convert_value(value):
        try:
            return ast.literal_eval(value)
        except Exception:
            return sympify(value)

    def get_domain(self, index):
        return self.domain[index]

    def get_format_expression(self):
        return latex(self.expr_original)

    def set_n_dimension(self, n):
        self.dimensions = int(n)
        self.expr = self.expr.subs('n', n)
        self.domain = self.browse_vector(self.domain, self.dimensions)
        self.location = self.browse_vector(self.location, self.dimensions)

    def calculate(self, v):
        value = self.expr
        if self.dimensions == Symbol('n') or self.dimensions <= 3:
            for index, val in enumerate(self.expr.free_symbols):
                try:
                    value = value.subs(val, v[index])
                except Exception as e:
                    print(value, val, v[index], e)
                    return float('inf')
            return float(value)
        else:
            v.insert(0, None)
            value = lambdify('x', value, ("math", "mpmath", "numpy", "sympy"))
            return value(v)

    def calculate_to_print_n(self, v):
        value = self.expr_original.subs('n', 2)
        try:
            v.insert(0, None)
            value = lambdify('x', value, ("math", "mpmath", "numpy", "sympy"))
            return value(v)
        except Exception as e:
            return float('inf')
