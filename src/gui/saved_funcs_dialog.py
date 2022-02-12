from sqlite3 import IntegrityError

from PyQt5 import QtWidgets, QtGui, QtCore

from .utils.utils_db import SavedFunctionsDB
from .utils.enums import EditMode
from .utils.utils import BadFormulaError
from .utils.utils_graphs import GraphFunction
from .designs.saved_funcs_dialog_design import Ui_Dialog as SavedFunctionDialogUi


class SavedFunctionsDialog(QtWidgets.QDialog, SavedFunctionDialogUi):

    def __init__(self, parent, saved_function_db_api: 'FunctionDB',
                 graph_func_setter):
        super(SavedFunctionsDialog, self).__init__(parent)
        self.saved_function_db_api = saved_function_db_api
        self.graph_func_setter = graph_func_setter
        self.items = []
        self.recently_clicked_item = None
        self.edit_item = None
        self.setupUi(self)

    def setupUi(self, Dialog):
        super().setupUi(Dialog)
        self.lineEditSearchFunc.setClearButtonEnabled(True)
        self.lineEditSearchFunc.addAction(QtGui.QIcon("resources/icons/saved_funcs/search.svg"),
                                          QtWidgets.QLineEdit.LeadingPosition)
        self.lineEditSearchFunc.setPlaceholderText('Поиск')
        self.lineEditSearchFunc.textChanged.connect(self.search_functions)
        self.lineEditSearchFunc.textChanged.emit(self.lineEditSearchFunc.text())

        self.listWidgetFunctions.itemDoubleClicked.connect(self.set_new_function)
        for i in range(self.listWidgetFunctions.count()):
            item = self.listWidgetFunctions.item(i)
            self.items.append((item, self.saved_function_db_api.get_id_by_func(item.text())))
        self.listWidgetFunctions.itemClicked.connect(self.start_edit_item)
        self.listWidgetFunctions.itemClicked.connect(self.mark_item)
        self.listWidgetFunctions.itemDelegate().closeEditor.connect(self.apply_item_changes)
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key.Key_Delete),
                            self).activated.connect(self.delete_items)
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key.Key_Backspace),
                            self).activated.connect(self.delete_items)

    def delete_items(self):
        selected_items = self.listWidgetFunctions.selectedItems()
        reply = QtWidgets.QMessageBox.question(self, 'Удалить', f'Вы уверены что хотите удалить '
                                                                f'функции в количестве '
                                                                f'{len(selected_items)} шт?')
        if reply == QtWidgets.QMessageBox.No:
            return
        for i in selected_items:
            ind_item = self.listWidgetFunctions.indexFromItem(i).row()
            self.saved_function_db_api.delete_func_by_id(
                self.saved_function_db_api.get_id_by_func(i.text()))
            self.listWidgetFunctions.takeItem(ind_item)

    def mark_item(self, item):
        self.recently_clicked_item = item

    def start_edit_item(self, item):
        if item != self.recently_clicked_item:
            return
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        item.setSelected(False)
        self.listWidgetFunctions.edit(self.listWidgetFunctions.indexFromItem(item))
        self.edit_item = item

    def apply_item_changes(self, editor):
        item = self.edit_item
        old_func = self.saved_function_db_api.get_func_by_id([i[1] for i in self.items
                                                              if i[0] == item][0])
        if item.text() == old_func:
            item.setFlags(item.flags() & (~QtCore.Qt.ItemIsEditable))
            self.edit_item = None
            self.recently_clicked_item = None
            editor.close()
            return
        reply = QtWidgets.QMessageBox.question(self,
                                               "Подтвердить",
                                               f"Вы точно хотетите изменить "
                                               f"{old_func} на {item.text()}?")
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                if not item.text():
                    raise BadFormulaError
                GraphFunction(item.text())
            except BadFormulaError:
                QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Неверная формула!')
            else:
                self.saved_function_db_api.update_func_by_id([i[1] for i in self.items
                                                              if i[0] == item][0], item.text())
        else:
            item.setText(old_func)
        item.setFlags(item.flags() & (~QtCore.Qt.ItemIsEditable))
        self.edit_item = None
        self.recently_clicked_item = None
        editor.close()

    def set_new_function(self, item):
        function = item.text()
        self.graph_func_setter(function)
        self.close()

    def search_functions(self, text):
        self.listWidgetFunctions.clear()
        if text == '':
            self.listWidgetFunctions.addItems(self.saved_function_db_api.get_all_func_from_db())
            return
        founded = self.saved_function_db_api.get_func_from_db(text)
        self.listWidgetFunctions.addItems(founded)


class FunctionDB(SavedFunctionsDB):

    def __init__(self, parent_widget=None):
        super(FunctionDB, self).__init__()
        self.parent = parent_widget
        self.function_backup = None
        self.edit_mode = EditMode.NoEdit

    def ask_to_save(self, graph_func: str):
        if self.edit_mode == EditMode.Edit:
            if self.function_backup[1] == graph_func:
                return
            title = "Подтвердить"
            text = f"Вы точно хотетите изменить " \
                   f"{self.function_backup[1]} на {graph_func}?"
        else:
            title = 'Сохранить?'
            text = f'Вы точно хотите сохранить функцию {graph_func}?'

        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Question, title,
                                    text,
                                    parent=self.parent)
        msg.addButton(QtWidgets.QMessageBox.Yes)
        msg.addButton(QtWidgets.QMessageBox.No)
        msg.setDefaultButton(QtWidgets.QMessageBox.No)
        msg.setIconPixmap(QtGui.QPixmap('resources/icons/saved_funcs/save.svg'))
        return msg.exec()

    def bad_formula_save_message(self):
        reply = QtWidgets.QMessageBox.warning(self.parent, 'Ошибка',
                                              'Введенная функция неверна,'
                                              ' поэтуму не будет сохранена.\nПродолжить?',
                                              QtWidgets.QMessageBox.Yes
                                              | QtWidgets.QMessageBox.No)
        return reply

    def save_func(self, graph_func: str, ask=True):
        try:
            GraphFunction(graph_func)
        except BadFormulaError:
            raise
        if ask:
            reply = self.ask_to_save(graph_func)
        else:
            reply = QtWidgets.QMessageBox.Yes
        if reply == QtWidgets.QMessageBox.No:
            return QtWidgets.QMessageBox.No
        if self.edit_mode == EditMode.Edit:
            if graph_func != self.function_backup[1]:
                self.change_func(graph_func)
        else:
            try:
                self.add_func_to_db(graph_func)
            except IntegrityError:
                QtWidgets.QMessageBox.warning(self.parent, 'Ошибка',
                                              'Такая функция уже сохранена')

    def change_func(self, new_func):
        if self.function_backup is None:
            return
        else:
            self.update_func_by_id(self.function_backup[0], new_func)

    def display_funcs(self, graph_func_setter):
        saved_functions_dialog = SavedFunctionsDialog(self.parent, self,
                                                      graph_func_setter)
        self.edit_mode = EditMode.PossibleEdit
        saved_functions_dialog.exec()

    def backup_func(self, graph_func: str):
        self.function_backup = self.get_id_by_func(graph_func), graph_func
