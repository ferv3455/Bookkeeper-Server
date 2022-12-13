import requests
import json
from time import time


def upload(accessToken, fileType, file):
    files = {'media': (f'{str(time)}.jpg', file)}
    data = {
            'access_token': accessToken,
            'type': fileType,
        }
    res = requests.post('https://api.weixin.qq.com/cgi-bin/media/upload', files=files, data=data)
    content = json.loads(res.text)
    if "media_id" in content:
        return content["media_id"]

    else:
        print(content)
        return None