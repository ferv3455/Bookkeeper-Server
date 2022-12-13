import hashlib
from lxml import etree
import time
from flask import make_response
import json

with open("/var/www/Bookkeeper-Server/appconfig.json", "r", encoding="utf-8") as fin:
    p = json.load(fin)
    APPID = p["appid"]
    APPSECRET = p["appsecret"]
    MESSAGE_TOKEN = p["messagetoken"]


class Message(object):
    def __init__(self, req):
        self.request = req
        self.AppID = APPID
        self.AppSecret = APPSECRET
        self.token = MESSAGE_TOKEN


class Get(Message):
    def __init__(self, req):
        super(Get, self).__init__(req)
        self.signature = req.args.get('signature')    # 这里分别获取传入的四个参数
        self.timestamp = req.args.get('timestamp')
        self.nonce = req.args.get('nonce')
        self.echostr = req.args.get('echostr')
        self.return_code = 'Invalid'

    def verify(self):
        try:
            data = sorted([self.token, self.timestamp, self.nonce])    # 字典排序
            string = ''.join(data).encode('utf-8')    # 拼接成字符串
            hashcode = hashlib.sha1(string).hexdigest()    # sha1加密

            if self.signature == hashcode:
                self.return_code = self.echostr

        except:
            # print(self.timestamp, self.nonce, self.echostr)
            pass

    def __str__(self) -> str:
        return "[GET] Request: "


class Post(Message):
    def __init__(self, req):
        super(Post, self).__init__(req)
        self.xml = etree.fromstring(req.stream.read())
        self.MsgType = self.xml.find("MsgType").text
        self.ToUserName = self.xml.find("ToUserName").text
        self.FromUserName = self.xml.find("FromUserName").text
        self.CreateTime = self.xml.find("CreateTime").text

        if self.MsgType == 'event':
            self.Event = self.xml.find("Event").text
            self.Content = 'New subscription'
            return

        self.MsgId = self.xml.find("MsgId").text

        content_list = {
            'text': ['Content'],
            'image': ['PicUrl', 'MediaId'],
            'voice': ['MediaId', 'Format'],
            'video': ['MediaId', 'ThumbMediaId'],
            'shortvideo': ['MediaId', 'ThumbMediaId'],
            'location': ['Location_X', 'Location_Y', 'Scale', 'Label'],
            'link': ['Title', 'Description', 'Url'],
        }

        attributes = content_list[self.MsgType]
        self.Content = self.xml.find(
            "Content").text if 'Content' in attributes else None
        self.PicUrl = self.xml.find(
            "PicUrl").text if 'PicUrl' in attributes else None
        self.MediaId = self.xml.find(
            "MediaId").text if 'MediaId' in attributes else None
        self.Format = self.xml.find(
            "Format").text if 'Format' in attributes else None
        self.ThumbMediaId = self.xml.find(
            "ThumbMediaId").text if 'ThumbMediaId' in attributes else None
        self.Location_X = self.xml.find(
            "Location_X").text if 'Location_X' in attributes else None
        self.Location_Y = self.xml.find(
            "Location_Y").text if 'Location_Y' in attributes else None
        self.Scale = self.xml.find(
            "Scale").text if 'Scale' in attributes else None
        self.Label = self.xml.find(
            "Label").text if 'Label' in attributes else None
        self.Title = self.xml.find(
            "Title").text if 'Title' in attributes else None
        self.Description = self.xml.find(
            "Description").text if 'Description' in attributes else None
        self.Url = self.xml.find("Url").text if 'Url' in attributes else None
        self.Recognition = self.xml.find(
            "Recognition").text if 'Recognition' in attributes else None

    def __str__(self) -> str:
        return "[POST] Request: FROM=%s TO=%s TIME=%s TYPE=%s" % (self.FromUserName, self.ToUserName, self.CreateTime, self.MsgType)


class Reply(Post):
    def __init__(self, req):
        super(Reply, self).__init__(req)
        self.xml = f'<xml><ToUserName><![CDATA[{self.FromUserName}]]></ToUserName>' \
                   f'<FromUserName><![CDATA[{self.ToUserName}]]></FromUserName>' \
                   f'<CreateTime>{str(int(time.time()))}</CreateTime>' \
                    '{}</xml>'
        self.content = ''

    def text(self, Content):
        self.content = f'<MsgType><![CDATA[text]]></MsgType>' \
                       f'<Content><![CDATA[{Content}]]></Content>'

    def image(self, MediaId):
        self.content = f'<MsgType><![CDATA[image]]></MsgType>' \
                       f'<Image><MediaId><![CDATA[{MediaId}]]></MediaId></Image>'

    def voice(self, MediaId):
        self.content = f'<MsgType><![CDATA[voice]]></MsgType>' \
                       f'<Voice><MediaId><![CDATA[{MediaId}]]></MediaId></Voice>'

    # def video(self, MediaId, Title, Description):
    #     pass

    # def music(self, ThumbMediaId, Title='', Description='', MusicURL='', HQMusicUrl=''):
    #     pass

    def reply(self):
        response = make_response(self.xml.format(self.content))
        response.content_type = 'application/xml'
        return response

    def __str__(self) -> str:
        return super().__str__() + " <Reply: %s>" % self.xml.format(self.content)
