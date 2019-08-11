import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap, QImage
import utils
import Visualization
import cv2
from PIL import Image
from wind import View, ActionReUI
import numpy as np
from mylog import logging, QPlainTextEditLogger


class ActionRe(ActionReUI):

    def __init__(self):
        super().__init__()
        self.timer.start(1000, self)
        self.views = []
        self.pose_visible = True
        self.data = {}
        h = QPlainTextEditLogger(None)
        self.log = logging.getLogger("Foo")
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(h)

    def timerEvent(self, a0):
        self.log.info('adwedwed')
        self.set_next_data()

    def btnClickedEvent(self, pressed):
        if pressed:
            self.btn.setText('no skeleton')
            self.pose_visible = False
            self.show_raw_images()
        else:
            self.btn.setText('show skeleton')
            self.pose_visible = True
            img_b, pose = self. data['img_b'], self.data['pose']
            img_np = np.frombuffer(img_b, Visualization.np.uint8)
            img_cv = cv2.imdecode(img_np, cv2.IMREAD_ANYCOLOR)
            self.draw_pose(img_cv, pose)

    def set_default_image(self):
        pix = QPixmap(960, 540)
        pix.fill(Qt.gray)
        self.lb.setPixmap(pix)

    def clear_views(self):
        for view in self.views:
            view.set_remove()
        self.views = []

    def show_raw_images(self):
        img_b = self.data['img_b']
        img_q = QImage.fromData(img_b)
        pix = QPixmap.fromImage(img_q)
        self.lb.setPixmap(pix)

    def draw_pose(self, img_cv: np.ndarray, pose: np.ndarray):
        if self.pose_visible and pose is not None:
            img_cv = Visualization.render(img_cv, pose, Visualization.RENDER_CONFIG_OPENPOSE, False)
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        pix = Image.fromarray(img_cv).toqpixmap()
        self.lb.setPixmap(pix)

    def set_data(self):
        data = utils.get_data()
        self.data = data
        self.clear_views()
        if data is None:
            self.timer.stop()
            self.set_default_image()

        else:
            img_b = data['img_b']
            pose = data['pose']
            img_np = np.frombuffer(img_b, Visualization.np.uint8)
            img_cv = cv2.imdecode(img_np, cv2.IMREAD_ANYCOLOR)
            # 大图
            self.draw_pose(img_cv, pose)
            # 小图
            for i in range(len(data['boundingBox'])):
                top, left, width, height = data['boundingBox'][i]
                img_flip = img_cv[top:top+height, left:left+width]
                img_flip = cv2.cvtColor(img_flip, cv2.COLOR_BGR2RGB)
                pix = Image.fromarray(img_flip).toqpixmap()
                person, action = data['nameAndAction'][i]
                view = View(self, pix, person, action)
                view.set_default_geometry()
                view.show()
                self.views.append(view)

    def set_next_data(self):
        self.set_data()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        if e.key() == Qt.Key_Space:
            pass


if __name__ == '__main__':


    app = QApplication(sys.argv)
    ex = ActionRe()

    ex.show()
    sys.exit(app.exec_())
