# coding=utf-8
from PyQt5.QtCore import QBasicTimer
import Utils
from PyQt5.QtCore import QObject
import Visualization
import cv2
import numpy as np


class Controller(QObject):
    def __init__(self, model, logger):
        super(Controller, self).__init__()
        self.__model = model
        self.__timer = QBasicTimer()
        self.__showSkeleton = True
        self.logger = logger

    def route(self, msg1, msg2):

        ''' 接收view的请求，并通过查找表调用对应的处理方法

        :param msg1: 响应view请求的方法名称
        :param msg2: 请求对应的参数(暂时没有用到)
        :return: 无
        '''

        {"startTimer": self.startTimer,
         "alterPoseState": self.alterPoseState,
         }[msg1](msg2)
        # log example
        self.logger.info('from {0}'.format(self.__class__.__name__))

    def alterPoseState(self, msg):
        if msg == "show skeleton":
            self.__showSkeleton = True
        else:
            self.__showSkeleton = False

    def startTimer(self, msg):
        ''' 开启定时器

        :param msg: 暂时用不到
        :return: 无
        '''
        self.__timer.start(25, self)

    def onSetData(self):
        ''' 获取数据，并更新model的数据

        :return: 无
        '''
        data = Utils.fetchData()
        processedData = self.processData(data)
        self.__model.setData(processedData)

    def processData(self, data):
        ''' 对获取到的数据做进一步的处理

        :param data:{
                    'img_b': 二进制图片,
                    'pose': ndarray,
                    'boundingBox': [[39, 917, 336, 886], [39, 917, 336, 886]],
                    'nameAndAction': [['葛某', '走'], ['葛某', '走']]
                    }
        :return:{
                'img': ndarray(根据self.__poseEnable决定，画上姿态的图片 or 原图),
                'boundingBox': [ndarray(未画上姿态的框内图片), ndarray(未画上姿态的框内图片)],
                'nameAndAction': [['葛某', '走'], ['葛某', '走']]
                }
        '''
        imgArray = np.frombuffer(data['img_b'], Visualization.np.uint8)
        imgNdarray = cv2.imdecode(imgArray, cv2.IMREAD_ANYCOLOR)
        imgNdarray = cv2.cvtColor(imgNdarray, cv2.COLOR_BGR2RGB)
        result = {
            'img': (self.drawPose(imgNdarray, data['pose']) if self.__showSkeleton else imgNdarray),
            'boundingBox': self.cutImage(imgNdarray, data['boundingBox']),
            'nameAndAction': data['nameAndAction']
        }

        return result

    def drawPose(self, imgNdarray: np.ndarray, pose: np.ndarray):
        imgNdarray = Visualization.render(imgNdarray, pose, Visualization.RENDER_CONFIG_OPENPOSE, False)
        return imgNdarray

    def cutImage(self, imgNdarray, boundingBoxs):
        cuts = []
        for boundingBox in boundingBoxs:
            top, left, width, height = boundingBox
            img_cut = imgNdarray[top:top + height, left:left + width]
            cuts.append(img_cut)
        return cuts

    def timerEvent(self, a0):
        self.onSetData()


if __name__ == '__main__':
    pass