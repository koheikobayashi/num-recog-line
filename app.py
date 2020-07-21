import numpy as np

from flask import Flask, request, abort

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage)

from keras.models import load_model
from keras.preprocessing import image

app = Flask(__name__)

ACCESS_TOKEN = "Sdr1mE+hoLx7RXtdreaAegInEBX33ktIrmNbvCG3bj64ELcpMWzJP7KfbgCK8voTTEvWdb/scFfYSaIeUaUUNocxDUAbb+rwoZBphwVpRF/mhlE+bt3dGrQ/5rlTY2+IhwwoWTpdHdr7v1CbJ7AeEgdB04t89/1O/w1cDnyilFU="
SECRET = "d1fec2f308c69fe2ff66481137cd3d64"

FQDN = "https://dogcat-test.herokuapp.com"


line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(SECRET)

model = load_model('dog_cat.h5')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Requestbody: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return'OK'


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    # 取得した画像ファイル
    with open("static/"+event.message.id+".jpg", "wb") as f:
        f.write(message_content.content)

        test_url = "./static/"+event.message.id+".jpg"

        img = image.load_img(test_url, target_size=(150, 150))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = x / 255.0

        result_predict = model.predict(x)

        if result_predict < 0.5:
            text = "This is cat"
        if result_predict >= 0.5:
            text = "This is dog"

        #line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=FQDN+"/static/"+event.message.id+".jpg",preview_image_url=FQDN+"/static/"+event.message.id+".jpg"))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text))

if __name__ == "__main__":
    app.run()
