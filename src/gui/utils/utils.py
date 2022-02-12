from keyword import iskeyword
from tokenize import (NAME, OP)
import csv

from sympy.assumptions.ask import AssumptionKeys
from sympy.core import Symbol
from sympy.core.basic import Basic
from sympy.core.function import Function
from sympy.parsing.sympy_parser import repeated_decimals, auto_number, \
    factorial_notation, convert_xor, convert_equals_signs, implicit_multiplication


class BadFormulaError(Exception):
    pass


def auto_single_symbol(tokens, local_dict, global_dict):
    """Inserts calls to ``Symbol``/``Function`` for undefined variables."""
    result = []
    prevTok = (None, None)

    tokens.append((None, None))  # so zip traverses all tokens
    for tok, nextTok in zip(tokens, tokens[1:]):
        tokNum, tokVal = tok
        nextTokNum, nextTokVal = nextTok
        if tokNum == NAME:
            name = tokVal

            if (name in ['True', 'False', 'None']
                    or iskeyword(name)
                    # Don't convert attribute access
                    or (prevTok[0] == OP and prevTok[1] == '.')
                    # Don't convert keyword arguments
                    or (prevTok[0] == OP and prevTok[1] in ('(', ',')
                        and nextTokNum == OP and nextTokVal == '=')
                    # the name has already been defined
                    or name in local_dict and local_dict[name] is not None):
                result.append((NAME, name))
                continue
            elif name in local_dict:
                local_dict.setdefault(None, set()).add(name)
                if nextTokVal == '(':
                    local_dict[name] = Function(name)
                else:
                    local_dict[name] = Symbol(name)
                result.append((NAME, name))
                continue
            elif name in global_dict:
                obj = global_dict[name]
                if isinstance(obj, (AssumptionKeys, Basic, type)) or callable(obj):
                    result.append((NAME, name))
                    continue

            for symbol in name:
                result.extend([
                    (NAME, 'Symbol' if nextTokVal != '(' else 'Function'),
                    (OP, '('),
                    (NAME, repr(str(symbol))),
                    (OP, ')'),
                ])
        else:
            result.append((tokNum, tokVal))

        prevTok = (tokNum, tokVal)

    return result


parse_transformations = (auto_single_symbol, repeated_decimals, auto_number,
                         factorial_notation, convert_xor,
                         convert_equals_signs,
                         implicit_multiplication)


def catmull_rom2bezier_svg(points, close=False):
    points = [j for i in points for j in i]
    i_len = len(points)
    points.extend([0, 0, 0, 0, 0, 0])
    d = []
    i = -2
    while i_len - 2 * (not close) > i:
        i += 2
        try:
            p = [[points[i - 2], points[i - 1]],
                 [points[i], points[i + 1]],
                 [points[i + 2], points[i + 3]],
                 [points[i + 4], points[i + 5]]]
        except IndexError:
            break
        if close:
            if not i:
                p[0] = [points[i_len - 2], points[i_len - 1]]
            elif i_len - 4 == i:
                p[3] = [points[0], points[1]]
            elif i_len - 2 == i:
                p[2] = [points[0], points[1]]
                p[3] = [points[2], points[3]]
        else:
            if i_len - 4 == i:
                p[3] = p[2]
            elif not i:
                p[0] = [points[i], points[i + 1]]

        bp = [
            'C',
            (-p[0][0] + 6 * p[1][0] + p[2][0]) / 6,
            (-p[0][1] + 6 * p[1][1] + p[2][1]) / 6,
            (p[1][0] + 6 * p[2][0] - p[3][0]) / 6,
            (p[1][1] + 6 * p[2][1] - p[3][1]) / 6,
            p[2][0],
            p[2][1]
        ]

        d.append(bp)

    return d[:-1]


def get_svg_paths(bezier_curves):
    svg_paths = []
    for curve in bezier_curves:
        curve_type, x1, y1, x2, y2, x, y = curve
        svg_path = f"{curve_type} {x1} {y1}, {x2} {y2}, {x} {y}"
        svg_paths.append(svg_path)
    return svg_paths


def get_curved_svg_from_points(points, color='red', closed=False):
    svg = """  
<svg viewBox="{} {} {} {}" xmlns="http://www.w3.org/2000/svg">
    <path d="{}" stroke="{}" fill="none" stroke-width="1%" transform="scale(1, -1)" 
    transform-origin="center"/>
</svg>
"""
    svg = svg.strip()
    max_x = max(i[0] for i in points)
    min_x = min(i[0] for i in points)
    max_y = max(i[1] for i in points)
    min_y = min(i[1] for i in points)
    width = max_x - min_x
    height = max_y - min_y
    start_point = f'M {points[0][0]} {points[0][1]} '
    paths_commands = catmull_rom2bezier_svg(points, closed)
    path = ' '.join(get_svg_paths(paths_commands))
    path = start_point + path
    svg = svg.format(min_x, abs(min_y), width, height, path, color)  # abs так отражаем по y
    return svg


def save_svg_from_points(points, save_path, color='red', closed=False):
    svg = get_curved_svg_from_points(points, color=color, closed=closed)
    with open(save_path, 'w') as f:
        f.write(svg)


def save_csv_points(points, save_path):
    f = open(save_path, 'w', newline='')
    writer = csv.writer(f, delimiter=',')
    header = ['x', 'y']
    writer.writerow(header)
    for point in points:
        writer.writerow(point)
    f.close()
