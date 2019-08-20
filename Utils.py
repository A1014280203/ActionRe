# coding=utf-8
import requests
import numpy as np
import os

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

URL = 'https://p2-1252380913.cos.ap-shanghai.myqcloud.com/sample.jpg'


def fetchData():
    try:
        resp = requests.get(URL, headers=headers)
    except Exception:
        return None
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
                'boundingBox': [[y, x, w, h]] * (i % 5 + 1),
                'nameAndAction': [['葛某', '走']] * (i % 5 + 1)}

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


# for test
fetchData = getLocalData()
# get_data = lambda: None


if __name__ == '__main__':
    # import cv2
    #
    # img_b = get_data()['img_b']
    # img_np = np.frombuffer(img_b, dtype=np.uint8)
    # img_cv = cv2.imdecode(img_np, cv2.IMREAD_ANYCOLOR)
    # img_clip = img_cv[39:39+886, 917:917+336]
    b = getLocalData()()
    print(b)
    print('a')
