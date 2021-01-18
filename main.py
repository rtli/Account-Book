import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog
from PyQt5.QtCore import pyqtSignal
from mainUi import Ui_Form
from sortUi import sortUi
from functools import partial
import csvIssue


class MyMainForm(QMainWindow, Ui_Form):
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
        if(not item or not sort or not price):
            self.response_Browser.setText("请正确输入噢 ;)")
        else:
            try:
                csvIssue.write_spending(item, sort, price)
                self.response_Browser.setText(
                    "记账成功!\n" + "你购买了属于"+sort+"品类下的"+item+",\n花费了"+price+"元.")
                self.tips_browser.setText("最近一次记账: "+item+" 金额: "+price+"元")
            except:
                self.response_Browser.setText("出错了 ;(")
        self.item_line.setText("")
        self.price_line.setText("")

    def generate(self):
        os.system("python diagram.py")
        res_code = QMessageBox.question(
            self, "生成成功", "立即查看？", QMessageBox.Yes | QMessageBox.No)
        if res_code != 65536:
            os.startfile("result.html")

    def withdraw(self):
        res_code = QMessageBox.question(
            self, "?", "确认撤销?", QMessageBox.Yes | QMessageBox.No)
        if res_code != 65536:
            flag = csvIssue.delete_last_line()
            if flag:
                QMessageBox.information(
                    self, 'Success', '成功删除', QMessageBox.Ok)
            else:
                QMessageBox.information(
                    self, 'Success', '记账记录已为空', QMessageBox.Ok)
            last_line = csvIssue.get_last_line()
            if not last_line:
                self.tips_browser.setText("记账记录为空!\n千里之行，始于足下。")
            else:
                self.tips_browser.setText(
                    "最近一次记账: "+str(last_line[0])+" 金额: "+str(last_line[2])+"元")
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

        self.first_add.clicked.connect(partial(self.add_classifier, 'first'))
        self.second_add.clicked.connect(partial(self.add_classifier, 'second'))

        self.first_delete.clicked.connect(partial(self.check_select, 'first'))
        self.second_delete.clicked.connect(
            partial(self.check_select, 'second'))

    def add_classifier(self, name):
        if name == 'second':
            second = self.second_line.text()
            first = self.second_Box.currentText()

        elif name == 'first':
            second = self.first_line.text()
            first = self.first_Box.currentText()

        else:
            QMessageBox.critical(self, "Error", "Error!", QMessageBox.Ok)
            return

        if first and second:
            flag = csvIssue.update_classifier(second, first)
            if flag:
                QMessageBox.information(
                    self, 'Success', '添加成功! ', QMessageBox.Ok)
                self.update_list()
            else:
                QMessageBox.information(
                    self, 'Duplicated', '项目已存在', QMessageBox.Ok)
            self.first_line.clear()
            self.second_line.clear()
        else:
            QMessageBox.critical(self, 'Error', '错误的参数', QMessageBox.Ok)

    def check_select(self, name):
        if name == 'first':
            items = [item.text()
                     for item in self.first_classifier.selectedItems()]
            if not items:
                QMessageBox.information(self, '?', '?', QMessageBox.Ok)
                return
        elif name == 'second':
            items = [item.text()
                     for item in self.second_classifier.selectedItems()]
            if not items:
                QMessageBox.information(self, '?', '?', QMessageBox.Ok)
                return
        self.delete_classifier(items)

    def update_list(self):
        first_classifier_list = csvIssue.init_first_classifier()
        second_classifier_list = csvIssue.init_second_classifier()

        self.first_classifier.clear()
        self.first_classifier.addItems(first_classifier_list)

        self.second_classifier.clear()
        self.second_classifier.addItems(second_classifier_list)

        self.second_Box.clear()
        self.second_Box.addItems(first_classifier_list)

        self._signal.emit(second_classifier_list)

    def delete_classifier(self, items):
        res_code = QMessageBox.question(
            self, "?", "确认删除?", QMessageBox.Yes | QMessageBox.No)
        if res_code == 65536:
            return
        else:
            flag = csvIssue.delete_classifier(items)
            if flag:
                self.update_list()
            else:
                QMessageBox.critical(
                    self, 'Error', '分类下存在记账记录', QMessageBox.Ok)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    myWin = MyMainForm()
    myWin.show()

    sys.exit(app.exec_())
