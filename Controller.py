# coding=utf-8
from PyQt5.QtCore import QBasicTimer
import Utils
from PyQt5.QtCore import QObject
import cv2
import numpy as np
# for tmp
from tmp import t


class Controller(QObject):
    def __init__(self, model, logger):
        super(Controller, self).__init__()
        self.__model = model
        self.__timer = QBasicTimer()
        self.logger = logger

    def route(self, msg1, msg2):

        ''' 接收view的请求，并通过查找表调用对应的处理方法

        :param msg1: 响应view请求的方法名称
        :param msg2: 请求对应的参数(暂时没有用到)
        :return: 无
        '''

        {"startTimer": self.startTimer}[msg1](msg2)
        # log example
        self.logger.info('from {0}'.format(self.__class__.__name__))

    def startTimer(self, msg):
        ''' 开启定时器
        :param msg: 暂时用不到
        '''
        self.__timer.start(40, self)

    def onSetData(self):
        ''' 获取数据，并更新model的数据

        :return: 无
        '''
        data = Utils.fetchData()
        processedData = self.processData(data)
        # for tmp
        if Utils.capture.isOpened():
            ret, frame = Utils.capture.read()
            processedData["img"] = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
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
                'img': ndarray,
                'pose': ndarray,
                'boundingBox': [[39, 917, 336, 886], [39, 917, 336, 886]],
                'nameAndAction': [['葛某', '走'], ['葛某', '走']]
                }
        '''
        imgArray = np.frombuffer(data.pop('img_b'), np.uint8)
        imgNdarray = cv2.imdecode(imgArray, cv2.IMREAD_ANYCOLOR)
        imgNdarray = cv2.cvtColor(imgNdarray, cv2.COLOR_BGR2RGB)
        data['img'] = imgNdarray
        return data

    def timerEvent(self, a0):
        self.onSetData()
