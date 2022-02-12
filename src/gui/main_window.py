from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraph import mkPen

from .designs.main_window_design import Ui_MainWindow
from .utils.enums import EditMode
from .utils.utils_graphs import GraphFunction
from .utils.utils import BadFormulaError
from .utils.utils_db import FunctionNotFound
from .saved_funcs_dialog import FunctionDB
from .graph_plot_widget import GraphPlotWidget
from .graph_animation import GraphAnimation
from .func_data_dialog import FunctionDataDialog


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    sigFormulaState = QtCore.pyqtSignal(bool)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.function_db = FunctionDB(self)
        self.setupUi(self)

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)

        self.setWindowIcon(QtGui.QIcon('resources/icons/main/parabola_512.png'))

        plt_widget = GraphPlotWidget(self.centralwidget)
        # заменяем заглушку на настоящий график-виджет
        self.gridLayout.replaceWidget(self.plotWidget,
                                      plt_widget)
        self.plotWidget = plt_widget

        self.graphsAnimationDockWidget = GraphAnimation(self.graphsAnimationDockWidget)
        self.graphsAnimationDockWidget.dock_widget.visibilityChanged.connect(
            self.actionShowAnimationDock.setChecked)

        self.graphsAnimationDockWidget.dock_widget.setVisible(False)

        self.formulaEdit.textChanged.connect(self.set_graph_function)

        self.sigFormulaState.emit(False)
        self.sigFormulaState.connect(self.set_formula_button)
        self.sigFormulaState.connect(self.actionShowAnimationDock.setEnabled)
        self.sigFormulaState.connect(self.update_graph_animation_dock)

        self.actionShowAnimationDock.triggered.connect(
            self.graphsAnimationDockWidget.dock_widget.setVisible)

        self.btnGraphInfo.clicked.connect(self.select_graph_color)

        self.sigFormulaState.connect(self.actionFunctionData.setEnabled)
        self.actionFunctionData.triggered.connect(self.show_function_data_dialog)

        self.sigFormulaState.connect(self.actionSaveFunc.setEnabled)
        self.actionSaveFunc.triggered.connect(self.save_function_to_db)

        self.actionLoadFunc.triggered.connect(self.load_function)

        self.formulaEdit.setText('y=2x^2+3x-5')

    def set_graph_function(self):
        if self.function_db.edit_mode == EditMode.AskEdit:
            self.ask_for_edit()
        function_string = self.formulaEdit.text()
        try:
            func = GraphFunction(function_string, 'y')
        except BadFormulaError as e:
            self.sigFormulaState.emit(False)
            if e.args == ('',):
                self.clear_graph()
        else:
            self.solve_possible_edit()
            self.plotWidget.graph_fn = func
            self.sigFormulaState.emit(True)

    def solve_possible_edit(self):
        if self.function_db.edit_mode == EditMode.PossibleEdit:
            try:
                self.function_db.backup_func(self.formulaEdit.text())
            except FunctionNotFound:
                self.function_db.edit_mode = EditMode.NoEdit
                return
            self.function_db.edit_mode = EditMode.AskEdit

    def exit_edit(self, obj, action):
        def inner():
            self.function_db.edit_mode = EditMode.NoEdit
            obj.removeAction(action)

        return inner

    def start_edit_mode(self):
        self.function_db.edit_mode = EditMode.Edit
        line_action = QtWidgets.QAction(QtGui.QIcon('resources/icons/main/edit.svg'), '')
        self.formulaEdit.addAction(line_action,
                                   QtWidgets.QLineEdit.LeadingPosition)
        menu_action = QtWidgets.QAction('Выйти из редактирования', self.menuFavoriteFunctions)
        exit_edit_mode_action = QtWidgets.QAction()
        exit_edit_mode_action.triggered.connect(self.exit_edit(self.formulaEdit, line_action))
        exit_edit_mode_action.triggered.connect(self.exit_edit(self.menuFavoriteFunctions,
                                                               menu_action))
        menu_action.triggered.connect(self.ask_to_exit_edit_mode(exit_edit_mode_action))
        self.menuFavoriteFunctions.addAction(menu_action)
        line_action.triggered.connect(self.ask_to_exit_edit_mode(exit_edit_mode_action))

    def ask_to_exit_edit_mode(self, action_to_trigger):
        def inner():
            reply = QtWidgets.QMessageBox.question(self, 'Подтвердить', 'Вы собираетесь'
                                                                        ' выйти из режима'
                                                                        ' редактирования,'
                                                                        ' продолжить?')
            if reply == QtWidgets.QMessageBox.Yes:
                action_to_trigger.trigger()
                try:
                    self.function_db.save_func(self.formulaEdit.text())
                except BadFormulaError:
                    reply = self.function_db.bad_formula_save_message()
                if reply == QtWidgets.QMessageBox.No:
                    self.start_edit_mode()

        return inner

    def ask_for_edit(self):
        reply = QtWidgets.QMessageBox.question(self, 'Изменить',
                                               'Хотите внести изменения в сохраненную функцию?')
        if reply == QtWidgets.QMessageBox.Yes:
            self.start_edit_mode()
        else:
            self.function_db.edit_mode = EditMode.NoEdit

    def clear_graph(self):
        self.plotWidget.graph_fn = None
        self.undo_bad_formula_info()
        self.btnGraphInfo.setDisabled(True)

    def undo_bad_formula_info(self):
        self.btnGraphInfo.setDisabled(False)
        self.btnGraphInfo.setIcon(QtGui.QIcon())

    def set_bad_formula_button(self):
        self.btnGraphInfo.setDisabled(True)
        icon_warn = QtGui.QIcon()
        icon_warn.addPixmap(self.style().standardPixmap(QtWidgets.QStyle.SP_MessageBoxWarning),
                            QtGui.QIcon.Mode.Disabled)
        self.btnGraphInfo.setIcon(icon_warn)

    def set_formula_button(self, state):
        if not state:
            self.set_bad_formula_button()
        else:
            self.undo_bad_formula_info()

    def select_graph_color(self):
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(255, 0, 0), self)
        if color.isValid():
            self.btnGraphInfo.setStyleSheet(
                "background-color: {}".format(color.name()))
            self.plotWidget.graph_pen = mkPen(color=color.getRgb(),
                                              width=self.plotWidget.graph_pen.width())
            self.plotWidget.update_graph()

    def update_graph_animation_dock(self, state):
        if not state:
            self.graphsAnimationDockWidget.dock_widget.setDisabled(True)
            return
        self.graphsAnimationDockWidget.dock_widget.setDisabled(False)
        self.graphsAnimationDockWidget.set_expr(self.plotWidget.graph_fn.sym_func)

    def show_function_data_dialog(self):
        dialog = FunctionDataDialog(self, self.plotWidget.graph_fn.sym_func)
        dialog.exec()

    def save_function_to_db(self):
        self.function_db.save_func(self.formulaEdit.text())

    def load_function(self):
        self.function_db.display_funcs(self.formulaEdit.setText)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        try:
            self.function_db.save_func(self.formulaEdit.text())
        except BadFormulaError:
            reply = self.function_db.bad_formula_save_message()
            if reply == QtWidgets.QMessageBox.No:
                a0.ignore()
                return
        a0.accept()
