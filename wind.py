import sys
from PyQt5.QtCore import Qt, QRect, QSize, QTimer, QBasicTimer
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QSlider,QFrame,
    QVBoxLayout, QApplication, QMainWindow, QHBoxLayout, QLabel, QGraphicsItem, QGridLayout)
from PyQt5.QtGui import QPixmap, QImage
import utils
import Visualization
import cv2
import matplotlib.pyplot as plt
import struct
from PIL import Image
from io import BytesIO
from io import BytesIO


class ActionRe(QWidget):

    def __init__(self):
        super().__init__()
        self.lb = QLabel(self)
        self.view_img = QLabel(self)
        self.view_tag_per = QLabel(self)
        self.view_tag_ac = QLabel(self)
        self.initUI()
        self.set_data()
        self.timer = QBasicTimer()
        self.timer.start(1000, self)

    def initUI(self):
        self.resize(1120, 630)

        self.lb.setLineWidth(0)
        self.lb.setGeometry(0, 0, 960, 540)
        self.lb.setStyleSheet("border: 0px")
        self.lb.setScaledContents(True)
        self.set_default_image()

        self.view_img.setGeometry(960+20, 15, 60, 60)
        self.view_tag_per.setGeometry(960+90, 20, 50, 20)
        self.view_tag_ac.setGeometry(960+90, 50, 50, 20)

        self.show()

    def timerEvent(self, a0):
        self.set_next_data()

    def set_default_image(self):
        pix = QPixmap(960, 540)
        pix.fill(Qt.gray)
        self.lb.setPixmap(pix)
        self.view_img.clear()

    def set_data(self):
        data = utils.get_data()

        if data is None:
            self.timer.stop()
            self.set_default_image()
            self.set_view_person()
            self.set_view_action()
        else:
            # 大图
            img_b = data['img_b']
            pose = data['pose']
            img_np = Visualization.np.frombuffer(img_b, Visualization.np.uint8)
            img_cv = cv2.imdecode(img_np, cv2.IMREAD_ANYCOLOR)
            img_cv = Visualization.render(img_cv, pose, Visualization.RENDER_CONFIG_OPENPOSE)
            cv2.imwrite('s.jpg', img_cv)
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
            pix = Image.fromarray(img_cv).toqpixmap()
            self.lb.setPixmap(pix)
            # 小图
            top, left, width, height = data['boundingBox']
            img_flip = img_cv[top:top+height, left:left+width]
            person, action = data['nameAndAction']
            self.set_view_image(Image.fromarray(img_flip).toqpixmap())
            self.set_view_person(person)
            self.set_view_action(action)

    def set_next_data(self):
        self.set_data()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        if e.key() == Qt.Key_Space:
            self.set_next_data()

    def set_view_image(self, img: QPixmap):
        w = img.size().width()
        h = img.size().height()
        if w > h:
            pix = img.scaledToWidth(60)
        else:
            pix = img.scaledToHeight(60)
        self.view_img.setPixmap(pix)

    def set_view_action(self, ac: str = ''):
        self.view_tag_ac.setText(ac)

    def set_view_person(self, per: str = ''):
        self.view_tag_per.setText(per)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ActionRe()
    ex.show()
    sys.exit(app.exec_())
