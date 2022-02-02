import os
import sys
from functools import partial

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox

import constants
import csv_handler
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
            self.response_Browser.setText(constants.tips_msg)
        else:
            try:
                csv_handler.write_spending(item, sort, price)
                self.response_Browser.setText(
                    constants.success_write_msg.format(
                        item=item, sort=sort, price=price
                    )
                )
                self.tips_browser.setText(
                    constants.recent_msg.format(item=item, price=price)
                )
            except Exception:
                self.response_Browser.setText(constants.error_msg)
        self.item_line.setText("")
        self.price_line.setText("")

    def generate(self):
        os.system("python diagram.py")
        res_code = QMessageBox.question(
            self,
            constants.success_generate_msg_head,
            constants.success_generate_msg_body,
            QMessageBox.Yes | QMessageBox.No,
        )
        if res_code != 65536:
            os.startfile("result.html")

    def withdraw(self):
        res_code = QMessageBox.question(
            self, "?", constants.confirm_withdraw_msg, QMessageBox.Yes | QMessageBox.No
        )
        if res_code != 65536:
            flag = csv_handler.delete_last_line()
            if flag:
                QMessageBox.information(
                    self, "Success", constants.success_delete_msg, QMessageBox.Ok
                )
            else:
                QMessageBox.information(
                    self, "Success", constants.empty_msg, QMessageBox.Ok
                )
            last_line = csv_handler.get_last_line()
            if not last_line:
                self.tips_browser.setText(constants.empty_record_msg)
            else:
                self.tips_browser.setText(
                    constants.recent_record_msg.format(
                        sort=str(last_line[0]),
                        price=str(
                            last_line[2],
                        ),
                    )
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

        self.first_add.clicked.connect(partial(self.add_classifier, "first"))
        self.second_add.clicked.connect(partial(self.add_classifier, "second"))

        self.first_delete.clicked.connect(partial(self.check_select, "first"))
        self.second_delete.clicked.connect(partial(self.check_select, "second"))

    def add_classifier(self, name):
        if name == "second":
            second = self.second_line.text()
            first = self.second_Box.currentText()

        elif name == "first":
            second = self.first_line.text()
            first = self.first_Box.currentText()

        else:
            QMessageBox.critical(self, "Error", "Error!", QMessageBox.Ok)
            return

        if first and second:
            flag = csv_handler.update_classifier(second, first)
            if flag:
                QMessageBox.information(
                    self, "Success", constants.success_add_msg, QMessageBox.Ok
                )
                self.update_list()
            else:
                QMessageBox.information(
                    self, "Duplicated", constants.error_duplicated_msg, QMessageBox.Ok
                )
            self.first_line.clear()
            self.second_line.clear()
        else:
            QMessageBox.critical(
                self, "Error", constants.error_invalid_params_msg, QMessageBox.Ok
            )

    def check_select(self, name):
        if name == "first":
            items = [item.text() for item in self.first_classifier.selectedItems()]
            if not items:
                QMessageBox.information(self, "?", "?", QMessageBox.Ok)
                return
        elif name == "second":
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
            self, "?", constants.confirm_delete_msg, QMessageBox.Yes | QMessageBox.No
        )
        if res_code == 65536:
            return
        else:
            flag = csv_handler.delete_classifier(items)
            if flag:
                self.update_list()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    constants.error_deleting_non_empty_classifier_msg,
                    QMessageBox.Ok,
                )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    myWin = MyMainForm()
    myWin.show()

    sys.exit(app.exec_())
