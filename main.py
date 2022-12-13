import io
import message as msg
from access import AccessToken
from resources import upload

from datetime import timedelta

from matplotlib import pyplot as plt
from flask import Flask, request
import json
# import mysql.connector

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
                # Text message: display data

                plt.figure()
                plt.plot([1, 2])
                plt.title("test")

                # Upload image
                buf = io.BytesIO()
                plt.savefig(buf, format='jpg')
                buf.seek(0)
                mediaId = upload(token.get(), 'image', buf)
                buf.close()

                # Reply
                if mediaId is not None:
                    message.image(mediaId)
                else:
                    message.text('系统错误，请稍后再试！')

        else:
            # Subscription event only
            message.text("欢迎关注fervor的试验田！随便回复些内容试试吧！")

        print(message)
        return message.reply()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
