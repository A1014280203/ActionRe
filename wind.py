import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QSlider,
    QVBoxLayout, QApplication, QMainWindow, QHBoxLayout, QLabel, QGraphicsItem)
from PyQt5.QtGui import QPixmap, QImage
import utils


class ActionRe(QMainWindow):

    def __init__(self):
        super().__init__()
        self.lb = QLabel(self)
        self.initUI()
        self.set_data()

    def set_default_image(self):
        pix = QPixmap(960, 540)
        pix.fill(Qt.gray)
        self.lb.setPixmap(pix)

    def set_data(self):
        data = utils.get_data()
        img_b = data['img_b']
        if img_b is None:
            self.set_default_image()
        else:
            img = QImage.fromData(img_b)
            pix = QPixmap.fromImage(img)
            self.lb.setPixmap(pix)

    def set_next_data(self):
        self.set_data()

    def initUI(self):
        self.resize(1120, 630)

        self.lb.setLineWidth(0)
        self.lb.setGeometry(0, 0, 960, 540)
        self.lb.setStyleSheet("border: 0px")

        self.set_default_image()

        self.show()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        if e.key() == Qt.Key_Space:
            self.set_next_data()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ActionRe()
    ex.show()
    sys.exit(app.exec_())
