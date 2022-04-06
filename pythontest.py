'''----------------------------------------------
@Project->File: ImageLabeller-master -> pythontest.py
@Author:ShawnPi
@Date:2022/4/6 18:54
----------------------------------------------'''
import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from father import Ui_MainWindow
from child import Ui_Dialog


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.onClicked)
        # 一定要在主窗口类的初始化函数中对子窗口进行实例化，如果在其他函数中实例化子窗口
        # 可能会出现子窗口闪退的问题
        self.ChildDialog = ChildWin()

    def onClicked(self):
        # print('打开子窗口！')
        self.ChildDialog.show()
        # 连接信号
        self.ChildDialog._signal.connect(self.getData)

    def getData(self, parameter, parameter1):
        # print('This is a test.')
        # print(parameter)
        self.lineEdit.setText(parameter)
        self.lineEdit_2.setText(parameter1)


class ChildWin(QMainWindow, Ui_Dialog):
    # 定义信号
    _signal = QtCore.pyqtSignal(str, str)

    def __init__(self):
        super(ChildWin, self).__init__()
        self.setupUi(self)
        self.retranslateUi(self)
        self.pushButton.clicked.connect(self.slot1)

    def slot1(self):
        data_str = self.lineEdit.text()
        data_str2 = self.lineEdit_2.text()
        # 发送信号
        self._signal.emit(data_str, data_str2)

        self.lineEdit.setText("")
        self.lineEdit_2.setText("")
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = MainWindow()
    ChildWindow = ChildWin()
    MainWindow.show()
    sys.exit(app.exec_())