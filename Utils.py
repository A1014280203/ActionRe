# coding=utf-8
import requests
import numpy as np
import os
import cv2
import json
import time


capture = cv2.VideoCapture(0)


def fetchData():
    resp = requests.get('')
    if resp.status_code == 200:
        pose = np.load('./1.npy', allow_pickle=True)[0, :2, 0, :].transpose(1, 0)
        return {'img_b': resp.content,
                'pose': pose,
                'boundingBox': [39, 917, 336, 886],
                'nameAndAction': ['葛某', '走']}
    else:
        return None


def getLocalData():
    imgs = os.listdir('./data/20_imga/')
    poses = np.load('./data/20.npy', allow_pickle=True)
    i = 0
    actions = ["唱", "跳", "rap", "篮球"]

    def iner():
        nonlocal imgs, i, poses
        if i >= len(imgs):
            i = 0
        with open('./data/20_imga/' + imgs[i], 'rb') as fr:
            img_b = fr.read()
        x, y, w, h = where2Cut(poses[0, :2, i, :])
        pose = poses[0, :2, i, :].transpose(1, 0)
        i += 1
        return {'img_b': img_b,
                'pose': pose,
                'boundingBox': [[y, x, w, h]],
                'nameAndAction': [['葛某', actions[int((i/5)) % 4]], ["蔡某", actions[int((i/5+1)) % 4]]]}

    return iner


def where2Cut(a: [[], []]):
    x, y = int(min(a[0]) * 1920), int(min(a[1]) * 1080)
    w = int((max(a[0]) - min(a[0])) * 1920)
    h = int((max(a[1]) - min(a[1])) * 1080)
    offsetX = 100
    offsetY = 50
    x = x - offsetX if x - offsetX > 0 else 0
    y = y - offsetY if y - offsetY > 0 else 0
    w = w + 2 * offsetX if x + w + 2 * offsetX < 1920 else 0
    h = h + 2 * offsetY if y + h + 2 * offsetY < 1080 else 0

    w, h = max(w, h), max(w, h)
    return x, y, w, h


class BehaviorRecord(object):

    __records = dict()
    __time = 0
    __fps = 0

    @classmethod
    def getRecords(cls):
        return cls.__records

    @classmethod
    def setFps(cls, fps):
        cls.__fps = fps

    @classmethod
    def lastActionOf(cls, name: str):
        if name not in cls.__records:
            return None
        return cls.__records[name][-1]["action"]

    @classmethod
    def record(cls, nameAndAction: [[], ]):
        """
        records = {
            "name": [
                {
                    "action": "唱",
                    "start": 0,
                    "end": 100
                },
            ],
        }
        """
        for n, a in nameAndAction:
            lastAction = cls.lastActionOf(n)
            if lastAction is None:
                cls.__records[n] = [{"action": a, "start": cls.__time, "end": cls.__time}, ]
            elif lastAction == a:
                cls.__records[n][-1]["end"] = cls.__time
            else:
                cls.__records[n].append({"action": a, "start": cls.__time, "end": cls.__time})
        cls.__time += 1

    @classmethod
    def theDurationOf(cls, d: dict):
        """

        :param d: {
                    "action": "唱",
                    "start": 0,
                    "end": 100
                }
        :return:
        """
        start, end = d["start"], d["end"]
        if cls.__fps == 0:
            return "0秒"
        d = (end - start)/cls.__fps
        if d > 3600:
            return f"{int(d//3600)}小时"
        elif d > 60:
            return f"{int(d//60)}分"
        else:
            return f"{int(d)}秒"


# for test
fetchData = getLocalData()
# get_data = lambda: None


if __name__ == '__main__':
    while capture.isOpened():
        # 获取一帧
        ret, frame = capture.read()
        print(capture.get(5))
        if ret:
            cv2.imshow('frame', frame)
        else:
            break
        if cv2.waitKey(1) == ord('q'):
            break
    capture.release()
    cv2.destroyAllWindows()
