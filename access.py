from message import APPID, APPSECRET
from time import time
import requests


class AccessToken:
    def __init__(self):
        self.token = None
        self.expire = None
        self.time = None

    def get(self):
        if self.token is not None and time() - self.time < self.expire:
            return self.token

        if self.update():
            return self.token

        return ""

    def update(self):
        data = {
            'grant_type': 'client_credential',
            'appid': APPID,
            'secret': APPSECRET,
        }
        res = requests.get('https://api.weixin.qq.com/cgi-bin/token', params=data)
        content = res.json()
        if "access_token" in content:
            self.token = content["access_token"]
            self.expire = content["expires_in"]
            self.time = time()
            return True

        else:
            print(content)
            return False
