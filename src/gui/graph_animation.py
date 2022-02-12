from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon
import sympy

from .utils.utils_graphs import GraphFunction
from .utils.enums import AnimDirection


class GraphAnimationItem(QtWidgets.QListWidgetItem):

    def __init__(self, parent,
                 plot_func_setter, before_expression, transformation):
        super().__init__(parent)
        self.plot_func_setter = plot_func_setter
        self.origin_expr = before_expression
        self.expr = before_expression
        self.transformation = transformation
        self.result_expr = self.get_result_expressions()
        # TODO: выделение трансформаций
        # label = QtWidgets.QLabel('{}->{}'.format(self.origin_expr,
        #                                          self.get_formatted_result_expression()))
        # label.setAcceptDrops(True)
        # self.listWidget().setItemWidget(self, label)
        self.setText('{}->{}'.format(self.origin_expr, self.result_expr))

        self.time_line_curve = QtCore.QEasingCurve.OutCubic
        self.time_line_back_curve = QtCore.QEasingCurve.InCubic

        self.timeline = QtCore.QTimeLine(1000)
        self.timeline.setEasingCurve(self.time_line_curve)
        self.timeline.setFrameRange(0, self.timeline.duration())
        self.timeline.setUpdateInterval(1)
        self.timeline.valueChanged.connect(self.update_graph)

    def get_formatted_result_expression(self, html_format='<b>{}</b>'):
        from_expr = self.origin_expr
        monom, (old, new) = self.transformation
        new = sympy.Symbol(html_format.format(new))
        transformations = monom, (old, new)
        res_expr = self.replace_coeff(from_expr, transformations)
        return res_expr

    def get_result_expressions(self):
        from_expr = self.origin_expr
        to_expr = self.replace_coeff(from_expr, self.transformation)
        return to_expr

    @staticmethod
    def replace_coeff(expr, transformation):
        monom, (old, new) = transformation
        poly = expr.as_poly()
        coeffs_dict = poly.as_dict()
        coeffs_dict[monom] = new
        poly = poly.from_dict(coeffs_dict, poly.gens)
        return poly.as_expr()

    def update_graph(self):
        monom, (old, new) = self.transformation
        new = (new - old) * self.timeline.currentValue() + old
        new_expression = self.replace_coeff(self.expr, (monom, (old, new)))
        func = GraphFunction(new_expression,
                             self.listWidget().parent().parent().parent().plotWidget.graph_fn.name)
        self.plot_func_setter(func)

    def setDirection(self, direction: QtCore.QTimeLine.Direction):
        if direction == QtCore.QTimeLine.Direction.Backward:
            self.timeline.setEasingCurve(self.time_line_back_curve)
        elif direction == QtCore.QTimeLine.Direction.Forward:
            self.timeline.setEasingCurve(self.time_line_curve)
        else:
            raise ValueError(f'Invalid direction {direction}. '
                             f'Only {QtCore.QTimeLine.Direction.Forward},'
                             f' {QtCore.QTimeLine.Direction.Backward} are possible')
        self.timeline.setDirection(direction)

    def start(self):
        self.expr = self.origin_expr
        self.timeline.start()

    def stop(self):
        self.timeline.stop()

    def clone(self):
        return self.__class__(None, self.plot_func_setter, self.origin_expr, self.transformation)


class GraphAnimation:

    def __init__(self, dock_widget, sympy_expression=None):
        self.dock_widget = dock_widget
        self.direction = AnimDirection.Forward
        self.direction_icons = {AnimDirection.Forward:
                                    'resources/icons/anim_params/right-arrow.svg',
                                AnimDirection.Backward:
                                    'resources/icons/anim_params/left-arrow.svg',
                                AnimDirection.Repeat:
                                    'resources/icons/anim_params/repeat.svg'}
        self.animation_list = self.dock_widget.parent().animationListWidget
        self.control_animation_btn = self.dock_widget.parent().btnShowAnimation
        self.control_button_icons = {QtCore.QTimeLine.State.Running:
                                         'resources/icons/anim_controls/pause.svg',
                                     QtCore.QTimeLine.State.NotRunning:
                                         'resources/icons/anim_controls/play.svg'}
        self.control_animation_btn_state = QtCore.QTimeLine.State.NotRunning
        self.direction_animation_btn = self.dock_widget.parent().btnAnimationDirection
        self.stop_animation_button = self.dock_widget.parent().btnStopAnimation
        self.label_expression = self.dock_widget.parent().labelExpression
        self.plot_widget = self.dock_widget.parent().plotWidget
        self.expr = sympy_expression if sympy_expression is not None else sympy.Expr()
        self.transformations = tuple()
        self.dragging_item = None
        self.protected_animations = []
        self.setupUi()

    def setupUi(self):
        self.updateUi()

        self.animation_list.setDragDropMode(self.animation_list.InternalMove)
        self.animation_list.setDragDropOverwriteMode(False)
        self.animation_list.dropEvent = self.drop_event_decorator(self.animation_list.dropEvent)
        self.animation_list.dragEnterEvent = self.drag_enter_event_decorator(
            self.animation_list.dragEnterEvent)

        direction_menu = self.get_direction_menu()
        self.direction_animation_btn.setMenu(direction_menu)

        self.control_animation_btn.clicked.connect(self.control_button_activate)
        self.stop_animation_button.clicked.connect(self.reset_to_start_animation)

        self.animation_list.itemDoubleClicked.connect(self.start_single_animation)

    def updateUi(self):
        if not self.expr.free_symbols:
            return
        self.animation_list.clear()
        self.label_expression.setText(sympy.maple_code(self.expr))
        self.transformations = self.get_base_transformations()
        self.add_animation_items()
        self.select_start_item()

    def drag_enter_event_decorator(self, func):
        def inner(e):
            func(e)
            items = e.source().selectedItems()
            if len(items) != 1:
                self.dragging_item = None
                return
            item = items[0]
            self.dragging_item = item

        return inner

    def drop_event_decorator(self, func):
        def inner(e):
            if self.dragging_item is None:
                func(e)
            else:
                self.drop_event_patch(e)
            self.update_transformations()
            self.reset_to_start_animation()

        return inner

    def drop_event_patch(self, e):
        prev_item = self.animation_list.itemAt(e.pos())
        prev_rect = self.animation_list.rectForIndex(self.animation_list.indexFromItem(prev_item))
        # если мышку отпустили на элементе списка так, что мышка находилась выше центра элемента, то
        # объект перетаскивания мы бросаем до элемента списка, иначе после
        if e.pos().y() > prev_rect.y() + prev_rect.height() // 2:
            drop_pos = 0  # ниже
        else:
            drop_pos = -1
        dragging_item = self.animation_list.takeItem(self.animation_list.row(self.dragging_item))
        ind = self.animation_list.row(prev_item) if prev_item else self.animation_list.count()
        prev_item = self.animation_list.takeItem(self.animation_list.row(prev_item))
        self.animation_list.insertItem(ind, dragging_item)
        self.animation_list.insertItem(ind - drop_pos, prev_item)
        self.animation_list.setCurrentItem(dragging_item)

    def get_direction_menu(self):
        menu = QtWidgets.QMenu()
        forward_action = QtWidgets.QAction(self.get_direction_icon(AnimDirection.Forward),
                                           'Прямо, по-порядку',
                                           self.direction_animation_btn)
        forward_action.triggered.connect(
            self.change_direction_decorator(AnimDirection.Forward))
        menu.addAction(forward_action)
        backward_action = QtWidgets.QAction(self.get_direction_icon(AnimDirection.Backward),
                                            'Обратно',
                                            self.direction_animation_btn)
        backward_action.triggered.connect(
            self.change_direction_decorator(AnimDirection.Backward))
        menu.addAction(backward_action)
        repeat_action = QtWidgets.QAction(self.get_direction_icon(AnimDirection.Repeat),
                                          'Зациклить',
                                          self.direction_animation_btn)
        repeat_action.triggered.connect(
            self.change_direction_decorator(AnimDirection.Repeat)
        )
        menu.addAction(repeat_action)
        return menu

    def get_direction_icon(self, direction):
        return QIcon(self.direction_icons[direction])

    def change_direction_decorator(self, direction):
        def inner():
            self.protected_animations.clear()
            self.direction = direction
            self.direction_animation_btn.setIcon(self.get_direction_icon(direction))
            self.reset_to_start_animation()

        return inner

    def deselect_items(self):
        for i in self.animation_list.selectedItems():
            i.setSelected(False)

    def select_start_item(self):
        self.deselect_items()
        start_item = self.get_start_item()
        if start_item is not None:
            start_item.setSelected(True)

    def get_base_expr(self):
        try:
            poly = self.expr.as_poly()
        except sympy.GeneratorsNeeded:
            return self.expr
        # FIXME: Проблема с коэффициентами функций (sin, sqrt) PolynomialError
        # TODO: парсер уравненения находящий все произведения с переменной
        first, *coeffs = poly.all_coeffs()
        coeffs = [1, ] + [0 for _ in coeffs]
        base_expr = poly.from_list(coeffs, poly.gens)
        return base_expr.as_expr()

    def get_base_transformations(self):
        base_expr_coeffs = self.get_base_expr().as_poly().all_coeffs()
        expr_coeffs = self.expr.as_poly().all_coeffs()
        transformations = tuple(
            zip(self.expr.as_poly().all_monoms(), zip(base_expr_coeffs, expr_coeffs)))
        return transformations

    def add_animation_items(self):
        transformations = self.transformations
        start_expr = self.get_base_expr()
        for transformation in transformations:
            _, (frm, to) = transformation
            if frm == to:  # бесполезные трансформации
                continue
            item = GraphAnimationItem(self.animation_list, self.plot_widget.set_graph_fn,
                                      start_expr, transformation)
            start_expr = item.result_expr

    def update_transformations(self):
        self.transformations = tuple(i.transformation for i in self.get_all_items())
        self.animation_list.clear()
        self.add_animation_items()
        self.select_start_item()

    def get_all_items(self):
        return [self.animation_list.item(i) for i in range(self.animation_list.count())]

    def disconnect_all_items(self):
        for i in self.get_all_items():
            try:
                i.timeline.finished.disconnect()
            except TypeError:
                pass
        for sig, slot in self.protected_animations:
            sig.connect(slot)

    def set_direction_to_all_items(self, direction):
        for i in self.get_all_items():
            i.setDirection(direction)

    def rotate_animation_items_if_last_animation_ended_decorator(self, item, direction_check,
                                                                 direction):
        def inner():
            if item.timeline.direction() != direction_check:
                return
            self.connect_animation_items(direction)
            item.start()

        return inner

    def connect_animation_items_repeat(self):
        self.connect_animation_items(AnimDirection.Forward)
        last_item = self.animation_list.item(self.animation_list.count() - 1)
        first_item = self.animation_list.item(0)
        if last_item is None or first_item is None:
            return
        lst_anim = self.rotate_animation_items_if_last_animation_ended_decorator(
            last_item,
            AnimDirection.Forward,
            AnimDirection.Backward)
        last_item.timeline.finished.connect(lst_anim)
        fst_anim = self.rotate_animation_items_if_last_animation_ended_decorator(
            first_item,
            AnimDirection.Backward,
            AnimDirection.Forward)
        first_item.timeline.finished.connect(fst_anim)
        self.protected_animations.extend([(last_item.timeline.finished, lst_anim),
                                          (first_item.timeline.finished, fst_anim)])

    def connect_animation_items(self, direction):
        # TODO: поддержка одновременных анимаций (QAction)
        if direction == AnimDirection.Backward:
            prev_items, next_items = (reversed(self.get_all_items()),
                                      reversed(self.get_all_items()[:-1]))
        elif direction == AnimDirection.Repeat:
            self.connect_animation_items_repeat()
            return
        else:
            prev_items, next_items = self.get_all_items(), self.get_all_items()[1:]
        self.disconnect_all_items()
        self.set_direction_to_all_items(direction)
        self.connect_items_states_and_button_state()
        for prev, nxt in zip(prev_items, next_items):
            prev.timeline.finished.connect(nxt.start)
            prev.timeline.finished.connect(self.individual_select_item_decorator(nxt))

    def connect_items_states_and_button_state(self):
        for i in self.get_all_items():
            i.timeline.stateChanged.connect(self.change_state_of_control_animation_btn)

    def change_state_of_control_animation_btn(self, state):
        # Между двумя изменениями состояний вообще то остановка
        # но это происходит так быстро, что это можно не обрабатывать
        icon_state = state
        if state != QtCore.QTimeLine.State.Running:
            icon_state = QtCore.QTimeLine.State.NotRunning
        icon = QIcon(self.control_button_icons[icon_state])
        self.control_animation_btn.setIcon(icon)
        self.control_animation_btn_state = state

    def individual_select_item_decorator(self, item):
        def inner():
            self.deselect_items()
            item.setSelected(True)

        return inner

    def stop_all_animations(self):
        for i in self.get_all_items():
            i.stop()
        self.change_state_of_control_animation_btn(QtCore.QTimeLine.State.NotRunning)

    def get_start_item(self):
        if self.direction == AnimDirection.Forward or self.direction == AnimDirection.Repeat:
            start_item = self.animation_list.item(0)
        else:
            start_item = self.animation_list.item(self.animation_list.count() - 1)
        return start_item

    def get_start_expr(self):
        if self.direction == AnimDirection.Forward or self.direction == AnimDirection.Repeat:
            start_item = self.animation_list.item(0)
            expr = start_item.expr
        else:
            start_item = self.animation_list.item(self.animation_list.count() - 1)
            expr = start_item.result_expr
        return expr

    def reset_to_start_animation(self):
        self.stop_all_animations()
        # self.plot_widget.set_graph_fn(GraphFunction(self.get_start_expr(),
        #                                             self.plot_widget.graph_fn.name))
        self.select_start_item()
        self.connect_animation_items(self.direction)

    def control_button_activate(self):
        if self.control_animation_btn_state == QtCore.QTimeLine.State.NotRunning:
            self.start_animation()
        elif self.control_animation_btn_state == QtCore.QTimeLine.State.Running:
            for i in self.get_all_items():
                if i.timeline.state() == QtCore.QTimeLine.State.Running:
                    i.timeline.setPaused(True)
        elif self.control_animation_btn_state == QtCore.QTimeLine.State.Paused:
            for i in self.get_all_items():
                if i.timeline.state() == QtCore.QTimeLine.State.Paused:
                    i.timeline.resume()

    def start_animation(self):
        # TODO: плавное перемещение от текущего к первой анимации
        self.reset_to_start_animation()
        start_item = self.get_start_item()
        if start_item is not None:
            start_item.start()

    def start_single_animation(self, item):
        if self.control_animation_btn_state != QtCore.QTimeLine.State.NotRunning:
            return
        self.stop_all_animations()
        self.disconnect_all_items()
        self.connect_items_states_and_button_state()
        item.start()

    def set_expr(self, expr):
        self.expr = expr
        self.updateUi()
