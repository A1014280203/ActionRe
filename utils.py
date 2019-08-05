import requests


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

URL = 'http://picture.ik123.com/uploads/allimg/170710/12-1FG0140P6.jpg'


def get_data():
    try:
        resp = requests.get(URL, headers=headers)
    except Exception:
        return None
    if resp.status_code == 200:
        return {'img_b': resp.content}
    else:
        return None
