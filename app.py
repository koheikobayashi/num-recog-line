from flask import Flask, request, abort

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent,TextMessage,TextSendMessage)


app = Flask(__name__)

ACCESS_TOKEN = "Sdr1mE+hoLx7RXtdreaAegInEBX33ktIrmNbvCG3bj64ELcpMWzJP7KfbgCK8voTTEvWdb/scFfYSaIeUaUUNocxDUAbb+rwoZBphwVpRF/mhlE+bt3dGrQ/5rlTY2+IhwwoWTpdHdr7v1CbJ7AeEgdB04t89/1O/w1cDnyilFU="
SECRET = "a7dce377ee7c51a6418d97ea36277175"


line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(SECRET)
@app.route("/callback",methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Requestbody: " + body)
    try:
        handler.handle(body,signature)
    except InvalidSignatureError:
        abort(400)

    return'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    app.run()
