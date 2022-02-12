import os

import sympy
from sympy import calculus

from .utils import save_svg_from_points, save_csv_points


class FunctionData:

    def __init__(self, expression):
        self.expr = expression
        self.var = self.expr.as_poly().args[1]
        self.features = list(self.get_features())

    def get_feature_domain(self):
        """Область определения. D(f): """
        domain = calculus.util.continuous_domain(self.expr, self.var,
                                                 sympy.S.Reals)
        return domain

    def get_feature_range(self):
        """Область значений. E(f): """
        rng = calculus.util.function_range(self.expr, self.var,
                                           sympy.S.Reals)
        return rng

    def get_feature_minimum(self):
        """Точка минимума: """
        return calculus.util.minimum(self.expr, self.var)

    def get_feature_maximum(self):
        """Точка максимума: """
        return calculus.util.maximum(self.expr, self.var)

    def get_features(self):
        for feature_getter in (getattr(self, i)
                               for i in self.__dir__()
                               if i != 'get_features' and i.startswith('get_feature')):
            try:
                value = feature_getter()
            except (TypeError, ValueError):
                value = 'Error'
            yield feature_getter.__doc__, value

    def get_pretty_features(self):
        pretty_features = ''
        for desc, val in self.features:
            str_val = sympy.pretty(val).strip()
            if '\n' in str_val:
                str_val += '\n' + str_val
            pretty_feature = desc + str_val + '\n'
            pretty_features += pretty_feature
        return pretty_features

    @staticmethod
    def _get_file_path(dir_path, extension):
        file_name = os.path.basename(dir_path) + f'.{extension.lstrip(".")}'
        file_path = os.path.join(dir_path, file_name)
        return file_path

    def save_features(self, dir_path):
        file_path = self._get_file_path(dir_path, 'txt')
        features = self.get_pretty_features()
        with open(file_path, 'w', encoding='utf8') as f:
            f.write(features)

    def save_image(self, visible_points, color, dir_path):
        file_path = self._get_file_path(dir_path, 'svg')
        save_svg_from_points(visible_points, file_path, color)

    def save_points_table(self, points, dir_path):
        file_path = self._get_file_path(dir_path, 'csv')
        save_csv_points(points, file_path)
