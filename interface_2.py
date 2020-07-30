
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QInputDialog, QGraphicsPixmapItem, \
    QGraphicsScene
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from QcureUi import cure
import tkinter.filedialog
import os
import cv2
import warnings
import os
warnings.filterwarnings("ignore")
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'

from main import run




content='1'
style='2'



class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(748, 377)
        self.graphicsView = QtWidgets.QGraphicsView(Form)
        self.graphicsView.setGeometry(QtCore.QRect(40, 80, 256, 192))
        self.graphicsView.setObjectName("graphicsView")
        self.graphicsView_2 = QtWidgets.QGraphicsView(Form)
        self.graphicsView_2.setGeometry(QtCore.QRect(420, 80, 256, 192))
        self.graphicsView_2.setObjectName("graphicsView_2")
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(104, 302, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(510, 302, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(Form)
        self.pushButton_3.setGeometry(QtCore.QRect(330, 150, 51, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setObjectName("pushButton_3")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton.setText(_translate("Form", "加载原图"))
        self.pushButton.clicked.connect(self.openFile_c)
        self.pushButton_2.setText(_translate("Form", "选择风格"))
        self.pushButton_2.clicked.connect(self.openFile_s)
        self.pushButton_3.setText(_translate("Form", "迁移"))
        self.pushButton_3.clicked.connect(self.transfer)


    def openFile_c(self):
        default_dir = r"F:"  # 设置默认打开目录
        global content
        content = tkinter.filedialog.askopenfilename(title=u"选择文件",
                                                   initialdir=(os.path.expanduser(default_dir)))
        print(content)
        img = cv2.imread(content)  # 读取图像
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 转换图像通道

        x = img.shape[1]  # 获取图像大小
        y = img.shape[0]
        img_nrows = 200
        img_ncols = int(y * img_nrows / x)
        img=cv2.resize(img,(img_nrows,img_ncols))
        frame = QImage(img, img_nrows, img_ncols, QImage.Format_RGB888)
        # frame = QImage(img, x, y, QImage.Format_RGB888)
        pix = QPixmap.fromImage(frame)
        self.item = QGraphicsPixmapItem(pix)
        self.scene = QGraphicsScene()
        self.scene.addItem(self.item)
        self.graphicsView.setScene(self.scene)

    def openFile_s(self):
        default_dir = r"F:"  # 设置默认打开目录
        global style
        style = tkinter.filedialog.askopenfilename(title=u"选择文件",
                                                   initialdir=(os.path.expanduser(default_dir)))
        print(style)
        img = cv2.imread(style)  # 读取图像
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 转换图像通道
        x = img.shape[1]  # 获取图像大小
        y = img.shape[0]
        img_nrows = 200
        img_ncols = int(y * img_nrows / x)
        img=cv2.resize(img,(img_nrows,img_ncols))
        frame = QImage(img, img_nrows, img_ncols, QImage.Format_RGB888)
        #frame = QImage(img, x, y, QImage.Format_RGB888)
        pix = QPixmap.fromImage(frame)
        self.item = QGraphicsPixmapItem(pix)
        self.scene = QGraphicsScene()
        self.scene.addItem(self.item)
        self.graphicsView_2.setScene(self.scene)


    def transfer(self):
        run(content,style)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_Form()
    ui.setupUi(MainWindow)
    win = cure.Windows(MainWindow,'?','?.jpg','blueGreen')
    sys.exit(app.exec_())