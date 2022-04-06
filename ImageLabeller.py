#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
图片浏览器
'''
__version__ = 0.4
import os
import sys
from datetime import datetime
import image_qr
from config_window import QConfig
from functools import partial
from PyQt5.QtGui import QPixmap, QTransform, QIcon, QFont, QCursor
from PyQt5.QtWidgets import (QFileDialog, QMainWindow, QApplication, QGraphicsScene,
                             QGraphicsView, QMenu, QMessageBox, QPushButton, QFormLayout, QWidget)
from PyQt5.QtCore import QDir, QFileInfo, Qt ,QTimer
import labeller
#from labeller import Ui_Labeller
import PyQt5.QtWidgets
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QFileDialog, QMainWindow, QApplication, QGraphicsScene,
                             QGraphicsView, QMenu, QMessageBox, QPushButton, QFormLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow,QHBoxLayout, QPushButton ,  QApplication, QWidget
import sys
import csv
import pandas as pd
class ImageViewer(QMainWindow):

    def __init__(self):
        super().__init__()
        self.tempKey=0
        self.formats = ('.png', '.jpg', '.jpeg', '.gif', '.bmp',
                        '.pbm', '.pgm', '.ppm', '.xbm', '.xpm')
        self.rotval = 0     # 旋转方向
        self.rotvals = (0, -90, -180, -270)
        self.file_path = QDir.currentPath()     # 获取当前文件路径

        self.resize(600, 800)
        self.setFixedSize(self.width(),self.height())
        self.setWindowTitle("Magic Viewer")
        self.setWindowIcon(QIcon(':/image/Icon.png'))

        self.btn = QPushButton("打开图片", self)
        self.btn.resize(200, 80)
        #self.btn.move((self.width() - self.btn.width()) / 2, (self.height() - self.btn.height()) / 2)
        self.btn.setFont(QFont("", 20, QFont.Bold))
        self.btn.clicked.connect(self.btnClicked)
        self.text=QtWidgets.QLineEdit()


        #菜单栏
        # 将ContextMenuPolicy设置为Qt.CustomContextMenu
        # 否则无法使用customContextMenuRequested信号
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # 创建QMenu信号事件
        self.customContextMenuRequested.connect(self.showMenu)
        self.menu = QMenu(self)
        self.function_menu=QMenu(self.menu)
        self.function_menu.setTitle('功能')
        self.open_menu = self.menu.addAction(QIcon(':/image/open.png'),'打开          O')
        self.file_path_menu = self.menu.addAction(QIcon(':/image/openfolder.png'),'打开文件所在位置')

        self.menu.addSeparator()
        self.menu.addMenu(self.function_menu)
        self.zoom_in_menu = self.function_menu.addAction(QIcon(':/image/zoom_in.png'), '放大          Scorll Up, W',)
        self.zoom_out_menu = self.function_menu.addAction(QIcon(':/image/zoom_out.png'), '缩小          Scroll Down, S')
        self.rotate_right_menu = self.function_menu.addAction(QIcon(':/image/rotate_right.png'), '顺转90°     R')
        self.rotate_left_menu = self.function_menu.addAction(QIcon(':/image/rotate_left.png'), '逆转90°     E')
        self.fitsize_menu = self.function_menu.addAction(QIcon(':/image/fitsize.png'),'适合屏幕    F')
        self.relsize_menu = self.function_menu.addAction(QIcon(':/image/relsize.png'),'实际尺寸    1')
        self.loop_menu = self.function_menu.addAction(QIcon(':/image/loop.png'), '幻灯片       L')
        self.about_menu = self.function_menu.addAction(QIcon(':/image/about.png'),'关于Magic Viewer')
        self.menu.addSeparator()
        self.next_menu = self.menu.addAction(QIcon(':/image/next.png'), '下一张       Right, SPACE')
        self.previous_menu = self.menu.addAction(QIcon(':/image/previous.png'), '上一张       Left, B')
        # self.search_menu = self.menu.addAction(QIcon(':/image/full.png'), '查找第n张图片          S')
        self.full_menu = self.menu.addAction(QIcon(':/image/full.png'), '全屏          F11')
        self.menu.addSeparator()
        self.close_menu=self.menu.addAction(QIcon(':/image/exit.png'),'退出')

       # 事件绑定
       #  self.zoom_in_menu.triggered.connect(self.zoomIn)
        self.zoom_out_menu.triggered.connect(self.zoomOut)
        self.full_menu.triggered.connect(self.toggleFullscreen)
        self.rotate_right_menu.triggered.connect(lambda: self.rotateImg(-1))
        self.rotate_left_menu.triggered.connect(lambda: self.rotateImg(1))
        self.next_menu.triggered.connect(lambda: self.dirBrowse(1))
        self.previous_menu.triggered.connect(lambda: self.dirBrowse(-1))
        # self.search_menu.triggered.connect(lambda: self.readCSV)
        self.fitsize_menu.triggered.connect(self.fitView)
        self.relsize_menu.triggered.connect(self.zoomReset)
        self.open_menu.triggered.connect(lambda: self.openfile(None))
        self.close_menu.triggered.connect(self.closeMainWindow)
        self.file_path_menu.triggered.connect(self.openfile_path)
        self.about_menu.triggered.connect(self.about)
        self.loop_menu.triggered.connect(self.loop_start)
        # 判断是否是幻灯片模式
        self.isLoop = False
        self.nowtime=datetime.now()

    def search(self):
        pass
    def readCSV(self):
        try:
            fname = 'my.csv'
            with open(fname, 'r', encoding='utf-8') as f:  # 打开文件
                lines = f.readlines()  # 读取所有行
                first_line = lines[0]  # 取第一行
                last_line = lines[-1]  # 取最后一行
                print('文件' + fname + '第一行为：' + first_line)
                print('文件' + fname + '最后一行为：' + last_line)

            with open(fname, 'rb') as f:  # 打开文件
                # 在文本文件中，没有使用b模式选项打开的文件，只允许从文件头开始,只能seek(offset,0)
                first_line = f.readline()  # 取第一行
                offset = -50  # 设置偏移量
                while True:
                    """
                    file.seek(off, whence=0)：从文件中移动off个操作标记（文件指针），正往结束方向移动，负往开始方向移动。
                    如果设定了whence参数，就以whence设定的起始位为准，0代表从头开始，1代表当前位置，2代表文件最末尾位置。
                    """
                    f.seek(offset, 2)  # seek(offset, 2)表示文件指针：从文件末尾(2)开始向前50个字符(-50)
                    lines = f.readlines()  # 读取文件指针范围内所有行
                    if len(lines) >= 2:  # 判断是否最后至少有两行，这样保证了最后一行是完整的
                        last_line = lines[-1]  # 取最后一行
                        break
                    # 如果off为50时得到的readlines只有一行内容，那么不能保证最后一行是完整的
                    # 所以off翻倍重新运行，直到readlines不止一行
                    offset *= 2
                print('文件' + fname + '第一行为：' + first_line.decode())
                print('文件' + fname + '最后一行为：' + last_line.decode())
            # with open("my.csv", "a", newline='') as f:
            #     filename="my.csv"
            #     df = pd.read_csv(filename, error_bad_lines=False) #error_bad_lines的优点是它将跳过并且不会在任何错误的行上打孔，但是如果最后一行总是无效，那么skipfooter=1更好
        except:
            QMessageBox.warning(self, "读取失败", "CSV文件正在被占用，请关闭后再试")
    def toCSV(self):
        try:
            with open("my.csv", "a", newline='') as f:
                writer = csv.writer(f)
                row =[self.title,self.tempKey]
                writer.writerow(row)
        except:
            QMessageBox.warning(self, "写入失败", "CSV文件正在被占用，请关闭后再试")
        # import csv
        # fileName = ".csv".format(self.nowtime)
        # with open(fileName,'w','utf-8')as csvfile:
        #     writer=csv.writer(csvfile)
        #     writer.writerow(['name','class'])
        #     writer.writerows([self.title,self.tempKey])
    def btnClicked(self):

        self.openfile()

    def openfile(self, file=None):
        if file is None:
            self.chooseFile()
        else:
            self.key = file.replace("\\", "/")
        # 获取图像列表
        if self.key:
            self.btn.setEnabled(False)      # 选择了文件按钮消失
            self.imgfiles = []  # 如果选择了文件则则重新获取图像列表
            self.file_path = os.path.dirname(self.key)      # 获取文件路径
            try:
                for file in os.listdir(self.file_path):
                    if os.path.splitext(file)[1].lower() in self.formats:
                        self.imgfiles.append(self.file_path + "/" + file)
                self.count = len(self.imgfiles)     # 图像列表总数量
                self.index = self.imgfiles.index(self.key)  # 当前图像在图像列表中位置
            except FileNotFoundError:
                print("文件目录不存在！")

        self.showImage()

    def chooseFile(self):
        # 选择图片文件
        self.key, _ = QFileDialog.getOpenFileName(self,
                                                  "选择文件", self.file_path,
                                                  "图片文件 (*.bmp *.jpg *.jpeg *.png *.gif)")
    def common_file(self,path):
        self.key, _ = QFileDialog.getOpenFileName(self,
                                                  "选择文件", path,
                                                  "图片文件 (*.bmp *.jpg *.jpeg *.png *.gif)")
        self.openfile(file=self.key)
    def openfile_path(self):
        #获得当前路径
        try:
            os.startfile(self.file_path)
        except FileNotFoundError:
            print("文件目录不存在！")

    def fitView(self):

        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        if self.rotate == 0:
            self.zoom = self.view.transform().m11()
        elif self.rotate == -90:
            self.zoom = (self.view.transform().m12()) * -1
        elif self.rotate == -180:
            self.zoom = (self.view.transform().m11()) * -1
        else:
            self.zoom = self.view.transform().m12()

    def showImage(self):

        if self.key:
            self.img = QPixmap(self.key)
            if self.img.isNull():
                QMessageBox.information(
                    self, "Magic Viewer", "不能打开文件：%s！" % self.key)
                return

            self.scene = QGraphicsScene()
            self.view = QGraphicsView(self.scene)
            self.view.setDragMode(QGraphicsView.ScrollHandDrag)
            # self.view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            # self.view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

            self.scene.clear()
            self.view.resetTransform()
            self.scene.addPixmap(self.img)


            self.zoom = 1   # 缩放系数
            self.rotate = 0  # 旋转系数

            # 如果图片尺寸＞窗口尺寸，计算缩放系数进行缩放
            if self.img.width() > self.width() or self.img.height() > self.height():
                self.zoom = min(self.width() / self.img.width(),
                                self.height() / self.img.height()) * 0.995

            width = self.img.width()
            height = self.img.height()

            # self.scene.setSceneRect(0, 0, width - 2, height - 2)
            self.view.resize(width, height)
            self.setCentralWidget(self.view)
            self.updateView()
            self.fitView()
            self.show()

    # 获取文件大小
    def fileSize(self, file):
        size = QFileInfo(file).size()

        if size < 1024:
            return str(size), "B"
        elif 1024 <= size < 1024 * 1024:
            return str(round(size / 1024, 2)), "KB"
        else:
            return str(round(size / 1024 / 1024, 2)), "MB"

    def closeMainWindow(self):

        self.close()

    def toggleFullscreen(self):
        # 全屏
        if self.isFullScreen():
            if self.isLoop:
                self.loop_end()
            else:
                self.showNormal()
        elif self.btn.isEnabled():#未全屏状态下如果任处启动界面，pass
            pass
        else:
            self.showFullScreen()

    def keyPressEvent(self, event):
        if self.isLoop:
            self.loop_end()
            return
        elif event.key() == Qt.Key_F11:
            self.toggleFullscreen()
        elif event.key() == Qt.Key_1:
            self.tempKey=1
            print("第"+str(self.index+1)+"张: "+self.title + " " + "1 Patch攻击")#Patch
            self.toCSV()
            self.dirBrowse(1)
        elif event.key() == Qt.Key_2:
            self.tempKey = 2
            self.toCSV()
            print("第"+str(self.index+1)+"张: "+self.title + " " + "2 对抗扰动")#对抗扰动
            self.dirBrowse(1)
        elif event.key() == Qt.Key_3:
            self.tempKey = 3
            self.toCSV()
            print("第"+str(self.index+1)+"张: "+self.title + " " + "3 轻微扰动")#轻微扰动
            self.dirBrowse(1)
        elif event.key() == Qt.Key_4:
            self.tempKey = 4
            self.toCSV()
            print("第"+str(self.index+1)+"张: "+self.title + " " + "4 正常样本")#正常样本
            self.dirBrowse(1)
        elif event.key() == Qt.Key_Up or event.key() == Qt.Key_W:
            self.zoomIn()
        elif event.key() == Qt.Key_Down or event.key() == Qt.Key_S:
            self.zoomOut()
        elif event.key() == Qt.Key_1:
            self.zoomReset()
        elif event.key() == Qt.Key_E:
            self.rotateImg(1)
        elif event.key() == Qt.Key_R:
            self.rotateImg(-1)
        elif event.key() == Qt.Key_F:
            self.fitView()
        elif event.key() == Qt.Key_Right or event.key() == Qt.Key_Space:
            self.tempKey = 4
            self.toCSV()
            print("第"+str(self.index+1)+"张: "+self.title + " " + "4 正常样本")#正常样本
            self.dirBrowse(1)
        elif event.key() == Qt.Key_Left or event.key() == Qt.Key_B:
            self.dirBrowse(-1)
        elif event.key() == Qt.Key_O:
            self.btnClicked()
        elif event.key()==Qt.Key_L:
            self.loop_start()
        elif event.key() == Qt.Key_Escape:
            self.showNormal()


    def mouseDoubleClickEvent(self, event):
        #定义左键双击鼠标事件
        self.toggleFullscreen()

    def zoomIn(self):

        self.zoom *= 1.05
        self.updateView()

    def zoomOut(self):

        self.zoom /= 1.05
        self.updateView()

    def zoomReset(self,):

        self.zoom = 1
        self.updateView()

    def rotateImg(self, clock):

        self.rotval += clock
        if self.rotval == 4:
            self.rotval = 0
        elif self.rotval < 0:
            self.rotval = 3
        self.rotate = self.rotvals[self.rotval]
        self.updateView()

    def fitView(self):

        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        if self.rotate == 0:
            self.zoom = self.view.transform().m11()
        elif self.rotate == -90:
            self.zoom = (self.view.transform().m12()) * -1
        elif self.rotate == -180:
            self.zoom = (self.view.transform().m11()) * -1
        else:
            self.zoom = self.view.transform().m12()

    def updateView(self):

        self.view.setTransform(QTransform().scale(
            self.zoom, self.zoom).rotate(self.rotate))
        # 更新标题信息
        self.title = os.path.basename(self.key)
        size = self.fileSize(self.key)
        self.setWindowTitle("%s(%sx%s,%s %s) - 第%s/%s张 %.2f%%" % (
            self.title, self.img.width(), self.img.height(), size[0], size[1],
            self.index + 1, self.count, self.zoom * 100))

    def dirBrowse(self, direc):

        if self.count > 1:
            self.index += direc
            # 最后一张后跳到第一张，第一张前跳到最后一张
            if self.index > self.count - 1:
                self.index = 0
            elif self.index < 0:
                self.index = self.count - 1

            self.key = self.imgfiles[self.index]

            self.showImage()

    def setBackground(self,color):
        #改变背景颜色
        # self.color = QColor(0, 0, 0)
        self.setStyleSheet('QWidget{background-color:%s}'%color)

    def loop_end(self):
        #关闭幻灯片
        if self.isLoop:

            self.timer.stop()
            self.setBackground('')#样式恢复默认效果
            self.isLoop = False
            self.showNormal()

    def loop_start(self):
        #开启幻灯片
        self.isLoop=True
        self.timer = QTimer()
        if self.isLoop:

            self.showFullScreen()
            self.setBackground('black')
            self.timer.start(5000)  # 每过5秒，定时器到期，产生timeout的信号
            self.timer.timeout.connect(partial(self.dirBrowse, 1))

    def wheelEvent(self, event):
        # 鼠标滚动
        moose = event.angleDelta().y() / 120
        if moose > 0:
            self.zoomIn()
        elif moose < 0:
            self.zoomOut()

    def showMenu(self):
        # 右键菜单
        if self.btn.isEnabled():
            common_menu = QMenu()
            qconfig = QConfig()
            common_menu.addAction(QIcon(':/image/config.png'), '配置', qconfig.show)
            path1,path2,path3=qconfig.read_config()
            if os.path.isdir(path1):
                common_menu.addAction(QIcon(':/image/common.png'), os.path.basename(path1), lambda :self.common_file(path1))
            if os.path.isdir(path2):
                common_menu.addAction(QIcon(':/image/common.png'), os.path.basename(path2), lambda :self.common_file(path2))
            if os.path.isdir(path3):
                common_menu.addAction(QIcon(':/image/common.png'), os.path.basename(path3), lambda :self.common_file(path3))
            common_menu.exec_(QCursor.pos())
        elif self.isLoop:
            self.loop_end()
            return
        else:
            self.menu.exec_(QCursor.pos())  # 在鼠标位置显示


    def about(self):
        QMessageBox.about(self, "关于Magic Viewer",
                          "<b>Magic Viewer</b>是一个基于PyQt5的开源图片浏览器<br>"
                          "三次作者 :ShawnPi"
                          "二次作者 : SkyZZF<br>"
                          "原作者 : Youth Lee<br>"
                          "版本 : Ver 0.4<br>"
                          "网址 : <a href='https://github.com/SkyZZF/MagicViewer'>https://github.com/SkyZZF/MagicViewer</a>")
    def showlog(self):
        logger=LabelLogger()
        logger.show()
class Ui_Labeller(ImageViewer):
    def setupUi(self, Labeller):
        Labeller.setObjectName("Labeller")
        Labeller.resize(415, 756)
        self.centralwidget = QtWidgets.QWidget(Labeller)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.logger = QtWidgets.QPlainTextEdit(self.centralwidget)
        # self.listView = QtWidgets.QListView(self.centralwidget)
        # self.listView.setObjectName("listView")
        self.verticalLayout.addWidget(self.logger)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btn_patchAtk = QtWidgets.QPushButton(self.centralwidget)
        self.btn_patchAtk.setObjectName("btn_patchAtk")
        self.horizontalLayout.addWidget(self.btn_patchAtk)
        self.btn_otherAtk = QtWidgets.QPushButton(self.centralwidget)
        self.btn_otherAtk.setObjectName("btn_otherAtk")
        self.horizontalLayout.addWidget(self.btn_otherAtk)
        self.btn_tinyAtk = QtWidgets.QPushButton(self.centralwidget)
        self.btn_tinyAtk.setObjectName("btn_noneAtk")
        self.horizontalLayout.addWidget(self.btn_tinyAtk)
        self.btn_nonAtk = QtWidgets.QPushButton(self.centralwidget)
        self.btn_nonAtk.setObjectName("btn_question")
        self.horizontalLayout.addWidget(self.btn_nonAtk)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        Labeller.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Labeller)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 415, 26))
        self.menubar.setObjectName("menubar")
        Labeller.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Labeller)
        self.statusbar.setObjectName("statusbar")
        Labeller.setStatusBar(self.statusbar)
        # self.toolBar = QtWidgets.QToolBar(Labeller)
        # self.toolBar.setObjectName("toolBar")
        # Labeller.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)

        self.retranslateUi(Labeller)
        QtCore.QMetaObject.connectSlotsByName(Labeller)



    def retranslateUi(self, Labeller):
        _translate = QtCore.QCoreApplication.translate
        Labeller.setWindowTitle(_translate("Labeller", "MainWindow"))
        self.btn_patchAtk.setText(_translate("Labeller", "Patch攻击 1"))
        self.btn_otherAtk.setText(_translate("Labeller", "对抗扰动 2"))
        self.btn_tinyAtk.setText(_translate("Labeller", "轻微攻击 3"))
        self.btn_nonAtk.setText(_translate("Labeller", "正常样本 4"))
        # self.toolBar.setWindowTitle(_translate("Labeller", "toolBar"))
class LabelLogger(Ui_Labeller,ImageViewer):
    def __init__(self):
        super(Ui_Labeller, self).__init__()
        super(LabelLogger, self).__init__()
        super(ImageViewer, self).__init__()
        self.setupUi(self)
        self.retranslateUi(self)
        self.isPatch()
        # 绑定按钮和键盘事件
        self.btn_patchAtk.clicked.connect(self.isPatch)
    def isPatch(self):
        #self.logger.appendPlainText(os.path.basename(self.key))
        self.logger.appendPlainText(self.title)
        print(super(self.title))
    def notAtk(self):
        self.listView.show()
        pass
    def isPatch(self):
        pass
    def otherAtk(self):
        pass



if __name__ == '__main__':

    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    # viewer.open(sys.argv[1])
    sys.exit(app.exec_())
