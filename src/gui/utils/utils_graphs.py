import warnings
from tokenize import TokenError

import sympy
from sympy.parsing import sympy_parser
from numpy import NaN

from .utils import parse_transformations, BadFormulaError


class GraphFunction:

    def __init__(self, function_string, name=None):
        if isinstance(function_string, sympy.Expr):
            self.sym_func = function_string
            self.func = sympy.lambdify(tuple(function_string.free_symbols) or ('_',),
                                       function_string)
            if name is None:
                raise ValueError('You should pass function name')
            self.name = name
            return

        # TODO: abs трансформация

        self.name = None
        self.sym_func = None
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', sympy.utilities.exceptions.SymPyDeprecationWarning)
                func = sympy_parser.parse_expr(function_string,
                                               transformations=parse_transformations)
        except SyntaxError as e:
            args = ()
            if e.args[-1][-1] == '':
                args = ('',)
            raise BadFormulaError(*args)
        except (NameError, TokenError, sympy.SympifyError, TypeError, AttributeError):
            raise BadFormulaError

        if isinstance(func, sympy.Eq):
            self.name = func.args[0]
            func = func.args[1]
            if isinstance(func, sympy.Symbol):
                self.name, func = func, self.name
        elif name is None:
            raise ValueError('You should pass function name')
        elif len(str(name)) != 1:
            raise ValueError('Name must have length that equals 1')
        elif not hasattr(func, 'free_symbols'):
            raise BadFormulaError
        else:
            self.name = name
        self.sym_func = func
        if len(tuple(func.free_symbols)) > 1:
            raise BadFormulaError
        self.func = sympy.lambdify(tuple(func.free_symbols) or ('_',), func)

    def __call__(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', RuntimeWarning)
            return self.func(*args, **kwargs)

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}={self.sym_func}')"

    def __str__(self):
        return f'{self.name}={self.sym_func}'


class NullGraphFunction:

    def __init__(self):
        self.name = ''
        self.sym_func = sympy.Expr()

    @staticmethod
    def func(x):
        x.fill(NaN)
        return x.copy()

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)