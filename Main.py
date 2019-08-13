# coding=utf-8
import sys
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QFrame, QPushButton
from PyQt5.QtGui import QPixmap, QImage
from Controller import Controller
from PyQt5.QtCore import pyqtSignal
from Model import Model
from PIL import Image
import time
from MyLog import logging, QPlainTextEditLogger
import Visualization
import numpy as np


# 自定义组件
class CaptureView(QFrame):

    __viewsCount = 0
    __views = []

    def __new__(cls, *args, **kwargs):
        cls.__viewsCount += 1
        ins = super().__new__(cls)
        cls.__views.append(ins)
        return ins

    def __init__(self, parent, img: QPixmap = None, person: str = '', action: str = ''):
        super().__init__(parent=parent)
        self.setObjectName(str(CaptureView.__viewsCount) + str(time.time()))
        self.__viewImg = QLabel(self)
        self.__viewTagPer = QLabel(self)
        self.__viewTagAc = QLabel(self)
        self.setImage(img)
        self.setTags(person, action)
        self.initUI()

    def initUI(self):
        self.__viewImg.setGeometry(20, 15, 60, 60)
        self.__viewTagPer.setGeometry(90, 20, 50, 20)
        self.__viewTagAc.setGeometry(90, 50, 50, 20)
        y = (CaptureView.__viewsCount - 1) * 90
        self.setGeometry(960, y, 160, 90)

    def setImage(self, img: QPixmap = None):
        if img is None:
            self.__viewImg.clear()
            return
        w = img.size().width()
        h = img.size().height()
        if w > h:
            pix = img.scaledToWidth(60)
        else:
            pix = img.scaledToHeight(60)
        self.__viewImg.setPixmap(pix)

    def setTags(self, per: str = '', ac: str = ''):
        self.__viewTagPer.setText(per)
        self.__viewTagAc.setText(ac)

    def setRemoveFlag(self):
        CaptureView.__viewsCount -= 1
        self.setParent(None)
        self.deleteLater()

    @classmethod
    def clearViews(cls):
        for v in cls.__views:
            v.setRemoveFlag()
        cls.__views = []


# 窗口
class ActionRe(QWidget):
    # 初始化成功的信号
    view2Contr = pyqtSignal(str, str)

    def __init__(self, model, logger: logging.Logger):
        super(QWidget, self).__init__()

        self.__model = model
        self.__model.dataChangedSignal.connect(self.getData)

        self.lb = QLabel(self)

        self.btn = QPushButton('no skeleton', self)
        self.btn.clicked.connect(self.buttonClicked)
        self.logger = logger
        self.__showSkeleton = True
        self.__data = None
        self.initUI()

    def initUI(self):
        self.resize(1120, 630)
        self.lb.setLineWidth(0)
        self.lb.setGeometry(0, 0, 960, 540)
        self.lb.setStyleSheet("border: 0px")
        self.lb.setScaledContents(True)

        self.btn.setCheckable(True)
        self.btn.setGeometry(20, 570, 150, 40)
        # log example
        self.logger.info('from {0}'.format(self.__class__.__name__))

    def getData(self):
        '''响应model数据更新信号，更新界面

        :return: 无
        '''
        self.__data = self.__model.getData()

        self.updataUI(self.__data)

    def updataUI(self, data):
        ''' 更新界面中的内容

        :param data:{
                'img': ndarray,
                'pose': ndarray,
                'boundingBox': [[39, 917, 336, 886], [39, 917, 336, 886]],
                'nameAndAction': [['葛某', '走'], ['葛某', '走']]
                }
        :return: 无
        '''
        # 先处理右侧小图
        CaptureView.clearViews()
        imgs = self.cutImage(data['img'], data['boundingBox'])
        nameAndActioins = data['nameAndAction']
        for img, tags in zip(imgs, nameAndActioins):
            CaptureView(self, Image.fromarray(img).toqpixmap(), *tags).show()
        # 处理大图
        img = data['img'].copy()
        if self.__showSkeleton:
            self.drawPose(img, data['pose'])
        pix = Image.fromarray(img).toqpixmap()
        self.lb.setPixmap(pix)

    def drawPose(self, imgNdarray: np.ndarray, pose: np.ndarray):
        imgNdarray = Visualization.render(imgNdarray, pose, Visualization.RENDER_CONFIG_OPENPOSE, True)
        return imgNdarray

    def cutImage(self, imgNdarray, boundingBoxs):
        cuts = []
        for boundingBox in boundingBoxs:
            top, left, width, height = boundingBox
            img_cut = imgNdarray[top:top + height, left:left + width]
            cuts.append(img_cut)
        return cuts

    def buttonClicked(self, pressed):
        # self.view2Contr.emit("alterPoseState", self.btn.text())
        if pressed:
            self.__showSkeleton = False
            self.btn.setText('show skeleton')
            self.updataUI(self.__data)
        else:
            self.__showSkeleton = True
            self.btn.setText('no skeleton')
            self.updataUI(self.__data)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    h = QPlainTextEditLogger(None)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(h)

    model = Model(logger)
    view = ActionRe(model, logger)
    controller = Controller(model, logger)

    # 视图更新完成，通知controller
    view.view2Contr.connect(controller.route)
    view.view2Contr.emit("startTimer", None)

    view.show()
    sys.exit(app.exec_())
