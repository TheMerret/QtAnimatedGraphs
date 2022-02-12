from PyQt5 import QtWidgets
from numpy import column_stack
from os import listdir

from .designs.func_data_dialog_design import Ui_Dialog as FuncDataDialogUi
from .utils.utils_function_data import FunctionData


class FunctionDataDialog(QtWidgets.QDialog, FuncDataDialogUi):

    def __init__(self, parent, expr):
        super(FunctionDataDialog, self).__init__(parent)
        self.function_data = FunctionData(expr)
        visible_points = parent.plotWidget.graphItem.getData()
        y_start = parent.plotWidget.visibleRange().y()
        y_finish = y_start + parent.plotWidget.visibleRange().height()
        visible_points = column_stack(visible_points)
        visible_points = visible_points[(y_start <= visible_points[:, 1]) &
                                        (visible_points[:, 1] <= y_finish)]
        color_hex = parent.plotWidget.graph_pen.color().name()
        self.data_savers = [('Свойства функции', self.function_data.save_features),
                            ('Изображение графика', lambda path:
                            self.function_data.save_image(visible_points, color_hex, path)),
                            ('Таблица точек функции', lambda path:
                            self.function_data.save_points_table(visible_points, path))]
        self.check_boxes = []
        self.setupUi(self)

    def setupUi(self, Dialog):
        super().setupUi(Dialog)
        icon_folder = self.style().standardIcon(QtWidgets.QStyle.SP_DirIcon)
        self.pushButtonOpenFileDialog.setIcon(icon_folder)
        for i, _ in self.data_savers:
            check_box = QtWidgets.QCheckBox(self)
            check_box.setText(i)
            self.layout().insertWidget(2, check_box)
            self.check_boxes.append(check_box)
        self.pushButtonOpenFileDialog.clicked.connect(self.get_folder)
        self.btnSave.clicked.connect(self.save_data)

    def get_folder(self):
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Выберите директорию', '',
                                                              options=
                                                              QtWidgets.QFileDialog.ShowDirsOnly)
        self.lineEditDirPath.setText(dir_path)

    def show_error(self, message):
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Ошибка")
        msg.setInformativeText(message)
        msg.setWindowTitle("Ошибка")
        msg.exec()

    def save_data(self):
        dir_path = self.lineEditDirPath.text()
        if not dir_path:
            self.show_error('Введите путь папки!')
            return
        if listdir(dir_path):
            self.show_error('Папка должна быть пустой!')
            return
        savers = [dict(self.data_savers)[i.text()] for i in self.check_boxes if i.isChecked()]
        if not savers:
            self.show_error('Выберите хотя бы один параметр!')
            return
        for saver in savers:
            saver.__call__(dir_path)
        close_msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,
                                          'Завершение', 'Готово',
                                          QtWidgets.QMessageBox.Ok, parent=self)
        close_msg.setText('Готово')
        close_msg.exec()
        close_msg.destroyed.connect(lambda: self.close())