# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'func_data_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(344, 318)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEditDirPath = QtWidgets.QLineEdit(Dialog)
        self.lineEditDirPath.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.lineEditDirPath.sizePolicy().hasHeightForWidth())
        self.lineEditDirPath.setSizePolicy(sizePolicy)
        self.lineEditDirPath.setReadOnly(True)
        self.lineEditDirPath.setObjectName("lineEditDirPath")
        self.horizontalLayout.addWidget(self.lineEditDirPath)
        self.pushButtonOpenFileDialog = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.pushButtonOpenFileDialog.sizePolicy().hasHeightForWidth())
        self.pushButtonOpenFileDialog.setSizePolicy(sizePolicy)
        self.pushButtonOpenFileDialog.setStyleSheet("background-color: rgba(239, 239, 239, 0);")
        self.pushButtonOpenFileDialog.setText("")
        self.pushButtonOpenFileDialog.setObjectName("pushButtonOpenFileDialog")
        self.horizontalLayout.addWidget(self.pushButtonOpenFileDialog)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.btnSave = QtWidgets.QPushButton(Dialog)
        self.btnSave.setObjectName("btnSave")
        self.horizontalLayout_2.addWidget(self.btnSave)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Сохранение данных функции"))
        self.pushButtonOpenFileDialog.setShortcut(_translate("Dialog", "Backspace"))
        self.btnSave.setText(_translate("Dialog", "Сохранить"))