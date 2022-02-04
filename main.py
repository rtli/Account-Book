import os
import sys
from functools import partial

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox

import constants
import csv_handler
from diagram import generate_diagram
from main_ui import UiForm
from sort_ui import sortUi


class MyMainForm(QMainWindow, UiForm):
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)
        self.sub = MySubForm()
        self.submit_button.clicked.connect(self.submit)
        self.generate_button.clicked.connect(self.generate)
        self.withdraw_button.clicked.connect(self.withdraw)
        self.edit_sort_button.clicked.connect(self.edit)

    def submit(self):
        item = self.item_line.text()
        sort = self.sort_line.currentText()
        price = self.price_line.text()
        if not item or not sort or not price:
            self.response_Browser.setText(constants.TIPS_MSG)
        else:
            try:
                csv_handler.write_spending(item, sort, price)
                self.response_Browser.setText(
                    constants.SUCCESS_WRITE_MSG.format(
                        item=item,
                        sort=sort,
                        price=price,
                    ),
                )
                self.tips_browser.setText(
                    constants.RECENT_MSG.format(
                        item=item,
                        price=price,
                    ),
                )
            except Exception:
                self.response_Browser.setText(constants.ERROR_MSG)
        self.item_line.setText("")
        self.price_line.setText("")

    def generate(self):
        generate_diagram()
        res_code = QMessageBox.question(
            self,
            constants.SUCCESS_GENERATE_MSG_HEAD,
            constants.SUCCESS_GENERATE_MSG_BODY,
            QMessageBox.Yes | QMessageBox.No,
        )
        if res_code != constants.PYQT_NEGATIVE_CODE:
            os.startfile(constants.RESULT_FILENAME)

    def withdraw(self):
        res_code = QMessageBox.question(
            self,
            "?",
            constants.CONFIRM_WITHDRAW_MSG,
            QMessageBox.Yes | QMessageBox.No,
        )
        if res_code != constants.PYQT_NEGATIVE_CODE:
            flag = csv_handler.delete_last_line()
            if flag:
                QMessageBox.information(
                    self,
                    constants.SUCCESS_HEAD,
                    constants.SUCCESS_DELETE_MSG,
                    QMessageBox.Ok,
                )
            else:
                QMessageBox.information(
                    self,
                    constants.SUCCESS_HEAD,
                    constants.EMPTY_MSG,
                    QMessageBox.Ok,
                )
            last_line = csv_handler.get_last_line()
            if not last_line:
                self.tips_browser.setText(constants.EMPTY_RECORD_MSG)
            else:
                self.tips_browser.setText(
                    constants.RECENT_RECORD_MSG.format(
                        sort=str(last_line[0]),
                        price=str(
                            last_line[2],
                        ),
                    ),
                )
            self.response_Browser.setText("")

    def edit(self):
        self.sub.show()
        self.sub._signal.connect(self.update_comboBox)

    def update_comboBox(self, plist):
        self.sort_line.clear()
        self.sort_line.addItems(plist)


class MySubForm(QDialog, sortUi):
    _signal = pyqtSignal(list)

    def __init__(self, parent=None):
        super(MySubForm, self).__init__(parent)
        self.setupUi(self)

        self.first_add.clicked.connect(
            partial(
                self.add_classifier,
                constants.FIRST,
            ),
        )
        self.second_add.clicked.connect(
            partial(
                self.add_classifier,
                constants.SECOND,
            ),
        )

        self.first_delete.clicked.connect(
            partial(
                self.check_select,
                constants.FIRST,
            ),
        )
        self.second_delete.clicked.connect(
            partial(
                self.check_select,
                constants.SECOND,
            ),
        )

    def add_classifier(self, name):
        if name == constants.SECOND:
            second = self.second_line.text()
            first = self.second_Box.currentText()

        elif name == constants.FIRST:
            second = self.first_line.text()
            first = self.first_Box.currentText()

        else:
            QMessageBox.critical(self, constants.ERROR_HEAD, "Error!", QMessageBox.Ok)
            return

        if first and second:
            flag = csv_handler.update_classifier(second, first)
            if flag:
                QMessageBox.information(
                    self,
                    constants.SUCCESS_HEAD,
                    constants.SUCCESS_ADD_MSG,
                    QMessageBox.Ok,
                )
                self.update_list()
            else:
                QMessageBox.information(
                    self,
                    constants.ERROR_DUPLICATED_HEAD,
                    constants.ERROR_DUPLICATED_MSG,
                    QMessageBox.Ok,
                )
            self.first_line.clear()
            self.second_line.clear()
        else:
            QMessageBox.critical(
                self,
                constants.ERROR_HEAD,
                constants.ERROR_INVALID_PARAMS_MSG,
                QMessageBox.Ok,
            )

    def check_select(self, name):
        if name == constants.FIRST:
            items = [item.text() for item in self.first_classifier.selectedItems()]
            if not items:
                QMessageBox.information(
                    self,
                    "?",
                    "?",
                    QMessageBox.Ok,
                )
                return
        elif name == constants.SECOND:
            items = [item.text() for item in self.second_classifier.selectedItems()]
            if not items:
                QMessageBox.information(self, "?", "?", QMessageBox.Ok)
                return
        self.delete_classifier(items)

    def update_list(self):
        first_classifier_list = csv_handler.init_first_classifier()
        second_classifier_list = csv_handler.init_second_classifier()

        self.first_classifier.clear()
        self.first_classifier.addItems(first_classifier_list)

        self.second_classifier.clear()
        self.second_classifier.addItems(second_classifier_list)

        self.second_Box.clear()
        self.second_Box.addItems(first_classifier_list)

        self._signal.emit(second_classifier_list)

    def delete_classifier(self, items):
        res_code = QMessageBox.question(
            self,
            "?",
            constants.CONFIRM_DELETE_MSG,
            QMessageBox.Yes | QMessageBox.No,
        )
        if res_code == constants.PYQT_NEGATIVE_CODE:
            return
        else:
            flag = csv_handler.delete_classifier(items)
            if flag:
                self.update_list()
            else:
                QMessageBox.critical(
                    self,
                    constants.ERROR_HEAD,
                    constants.ERROR_DELETING_NON_EMPTY_CLASSIFIER_MSG,
                    QMessageBox.Ok,
                )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    myWin = MyMainForm()
    myWin.show()

    sys.exit(app.exec_())
