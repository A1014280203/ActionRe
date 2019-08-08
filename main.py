import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap
import utils
import Visualization
import cv2
from PIL import Image
from wind import View, ActionReUI


class ActionRe(ActionReUI):

    def __init__(self):
        super().__init__()
        self.timer.start(1000, self)
        self.views = []

    def timerEvent(self, a0):
        self.set_next_data()

    def set_default_image(self):
        pix = QPixmap(960, 540)
        pix.fill(Qt.gray)
        self.lb.setPixmap(pix)

    def clear_views(self):
        for view in self.views:
            view.set_remove()
        self.views = []

    def set_data(self):
        data = utils.get_data()
        if data is None:
            self.timer.stop()
            self.set_default_image()
        else:
            self.clear_views()
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
            for i in range(len(data['boundingBox'])):
                top, left, width, height = data['boundingBox'][i]
                img_flip = img_cv[top:top+height, left:left+width]
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ActionRe()
    ex.show()
    sys.exit(app.exec_())
