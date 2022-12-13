from datetime import timedelta
import json

from flask import Flask, request

import message as msg
from access import AccessToken
from resources import upload
from accounting import lookup, graph, insert


app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
with open("/var/www/Bookkeeper-Server/appconfig.json", "r", encoding="utf-8") as fin:
    p = json.load(fin)
    app.secret_key = p["secretkey"]


##############################################################################
# Wechat Official Account #
##############################################################################

token = AccessToken()

@app.route("/")
def index():
    '''Index Page'''
    return "<h1>Welcome!</h1>"


@app.route("/wechat/message/", methods=["GET", "POST"])
def wechat_message_response():
    '''Process Wechat Official Account Messages.'''
    if request.method == "GET":
        message = msg.Get(request)
        message.verify()
        print(message)
        return message.return_code

    elif request.method == "POST":
        message = msg.Reply(request)
        if message.MsgType != 'event':
            if message.Content:
                content = message.Content.split()
                if content[0] == "查询":
                    buf = lookup(content[1:])
                    buf.seek(0)
                    mediaId = upload(token.get(), 'image', buf)
                    buf.close()
                    if mediaId is not None:
                        message.image(mediaId)
                    else:
                        message.text('系统错误，请稍后再试！')
                elif content[0] == "绘图":
                    buf = graph(content[1:])
                    buf.seek(0)
                    mediaId = upload(token.get(), 'image', buf)
                    buf.close()
                    if mediaId is not None:
                        message.image(mediaId)
                    else:
                        message.text('系统错误，请稍后再试！')
                elif content[0] == "添加" or content[0] == "插入":
                    res = insert(content[1:])
                    if res:
                        message.text('添加成功')
                    else:
                        message.text('系统错误，请稍后再试！')
                else:
                    message.text('未知操作：' + message.Content)

        else:
            # Subscription event only
            message.text("欢迎关注fervor的试验田！随便回复些内容试试吧！")

        print(message)
        return message.reply()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
