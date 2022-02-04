# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'final.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator

import constants
import csv_handler

classifier = csv_handler.init_second_classifier()


class UiForm(object):
    def setupUi(self, Form):
        Form.setObjectName(constants.MAIN_SCENE)
        Form.resize(620, 420)
        Form.setMinimumSize(QtCore.QSize(620, 420))
        Form.setMaximumSize(QtCore.QSize(620, 420))
        font = QtGui.QFont()
        font.setFamily(constants.MICROSOFT_YAHEI)
        Form.setFont(font)
        Form.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        Form.setMouseTracking(False)
        self.submit_button = QtWidgets.QPushButton(Form)
        self.submit_button.setGeometry(QtCore.QRect(100, 300, 82, 62))
        font = QtGui.QFont()
        font.setFamily(constants.SOURCE_HAN_SANS_BOLD)
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.submit_button.setFont(font)
        self.submit_button.setObjectName(constants.FIRST_SUBMIT_BUTTON)
        self.generate_button = QtWidgets.QPushButton(Form)
        self.generate_button.setGeometry(QtCore.QRect(220, 300, 82, 62))
        font = QtGui.QFont()
        font.setFamily(constants.SOURCE_HAN_SANS_BOLD)
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.generate_button.setFont(font)
        self.generate_button.setObjectName(constants.SECOND_SUBMIT_BUTTON)
        self.item_line = QtWidgets.QLineEdit(Form)
        self.item_line.setGeometry(QtCore.QRect(100, 70, 201, 31))
        font = QtGui.QFont()
        font.setFamily(constants.MICROSOFT_YAHEI)
        font.setPointSize(14)
        self.item_line.setFont(font)
        self.item_line.setText("")
        self.item_line.setObjectName(constants.ITEM_LINE)
        self.item_line.setMaxLength(10)
        self.item_line.setPlaceholderText(constants.PLACEHOLDER_ITEM)
        self.price_line = QtWidgets.QLineEdit(Form)
        self.price_line.setGeometry(QtCore.QRect(100, 230, 201, 31))
        font = QtGui.QFont()
        font.setFamily(constants.MICROSOFT_YAHEI)
        font.setPointSize(14)
        self.price_line.setFont(font)
        self.price_line.setText("")
        self.price_line.setObjectName(constants.PRICE_LINE)
        regex = QRegExp(r"^[0-9]+(\.[0-9]{1,2})?$")
        validator = QRegExpValidator(regex, self.price_line)
        self.price_line.setValidator(validator)
        self.price_line.setMaxLength(13)
        self.price_line.setPlaceholderText(constants.PLACEHOLDER_PRICE)
        self.sort_line = QtWidgets.QComboBox(Form)
        self.sort_line.setGeometry(QtCore.QRect(100, 150, 201, 31))
        self.sort_line.setObjectName(constants.SORT_LINE)
        self.sort_line.setFont(font)
        self.sort_line.setObjectName(constants.SORT_LINE)
        if classifier:
            self.sort_line.addItem(classifier[0])
            if len(classifier) > 1:
                self.sort_line.addItems(classifier[1:])
        self.item_label = QtWidgets.QLabel(Form)
        self.item_label.setGeometry(QtCore.QRect(20, 70, 61, 31))
        font = QtGui.QFont()
        font.setFamily(constants.SOURCE_HAN_SANS_MEDIUM)
        font.setPointSize(18)
        font.setBold(False)
        font.setWeight(50)
        self.item_label.setFont(font)
        self.item_label.setObjectName(constants.ITEM_LABEL)
        self.sort_label = QtWidgets.QLabel(Form)
        self.sort_label.setGeometry(QtCore.QRect(20, 150, 61, 31))
        font = QtGui.QFont()
        font.setFamily(constants.SOURCE_HAN_SANS_MEDIUM)
        font.setPointSize(18)
        font.setBold(False)
        font.setWeight(50)
        self.sort_label.setFont(font)
        self.sort_label.setObjectName(constants.SORT_LABEL)
        self.price_label = QtWidgets.QLabel(Form)
        self.price_label.setGeometry(QtCore.QRect(20, 230, 61, 31))
        font = QtGui.QFont()
        font.setFamily(constants.SOURCE_HAN_SANS_MEDIUM)
        font.setPointSize(18)
        font.setBold(False)
        font.setWeight(50)
        self.price_label.setFont(font)
        self.price_label.setObjectName(constants.PRICE_LABEL)
        self.tips_browser = QtWidgets.QTextBrowser(Form)
        self.tips_browser.setGeometry(QtCore.QRect(330, 40, 256, 61))
        self.tips_browser.setObjectName(constants.TIPS_BROWSER)
        font = QtGui.QFont()
        font.setFamily(constants.MICROSOFT_YAHEI)
        font.setPointSize(14)
        self.tips_browser.setFont(font)
        last_line = csv_handler.get_last_line()
        if not last_line:
            self.tips_browser.setText(constants.EMPTY_RECORD_MSG)
        else:
            self.tips_browser.setText(
                constants.RECENT_MSG.format(
                    item=str(last_line[0]),
                    price=str(last_line[2]),
                ),
            )
        self.widget = QtWidgets.QWidget(Form)
        self.widget.setGeometry(QtCore.QRect(420, 280, 86, 111))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.edit_sort_button = QtWidgets.QPushButton(self.widget)
        font = QtGui.QFont()
        font.setFamily(constants.SOURCE_HAN_SANS_BOLD)
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.edit_sort_button.setFont(font)
        self.edit_sort_button.setObjectName(constants.EDIT_SORT_BUTTON)
        self.verticalLayout.addWidget(self.edit_sort_button)
        self.withdraw_button = QtWidgets.QPushButton(self.widget)
        font = QtGui.QFont()
        font.setFamily(constants.SOURCE_HAN_SANS_BOLD)
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.withdraw_button.setFont(font)
        self.withdraw_button.setObjectName(constants.WITHDRAW_BUTTON)
        self.verticalLayout.addWidget(self.withdraw_button)
        self.response_Browser = QtWidgets.QTextBrowser(Form)
        self.response_Browser.setGeometry(QtCore.QRect(330, 150, 256, 121))
        self.response_Browser.setObjectName(constants.RESPONSE_BROWSER)
        font = QtGui.QFont()
        font.setFamily(constants.MICROSOFT_YAHEI)
        font.setPointSize(14)
        self.response_Browser.setFont(font)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate(constants.FORM, "主界面"))
        self.setWindowIcon(QtGui.QIcon("./images/icon.png"))
        self.submit_button.setText(_translate(constants.FORM, "提交"))
        self.item_label.setText(_translate(constants.FORM, "名称:"))
        self.sort_label.setText(_translate(constants.FORM, "分类:"))
        self.price_label.setText(_translate(constants.FORM, "金额:"))
        self.generate_button.setText(_translate(constants.FORM, "生成"))
        self.edit_sort_button.setText(_translate(constants.FORM, "编辑分类"))
        self.withdraw_button.setText(_translate(constants.FORM, "撤销提交"))
