# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'saved_funcs_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lineEditSearchFunc = QtWidgets.QLineEdit(Dialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEditSearchFunc.setFont(font)
        self.lineEditSearchFunc.setObjectName("lineEditSearchFunc")
        self.verticalLayout.addWidget(self.lineEditSearchFunc)
        self.listWidgetFunctions = QtWidgets.QListWidget(Dialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.listWidgetFunctions.setFont(font)
        self.listWidgetFunctions.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.listWidgetFunctions.setEditTriggers(QtWidgets.QAbstractItemView.CurrentChanged)
        self.listWidgetFunctions.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidgetFunctions.setObjectName("listWidgetFunctions")
        self.verticalLayout.addWidget(self.listWidgetFunctions)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Сохраненные функции"))