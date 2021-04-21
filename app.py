import numpy as np

from flask import Flask, request, abort

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage)

from keras.preprocessing import image
from tensorflow.keras.models import load_model
from PIL import Image




app = Flask(__name__)

ACCESS_TOKEN = "gbU9ngnEG3tWv99t6pqmCo4eXDaWkEO0TBbFk7ML3LfrTw1A6eGXtjklverSbhJI4XUcVp0/XzFZxeMsFSvBqWLvbdJMqsU7dnQqSdTtWdN2cH2W4mEBD+WRZluLijX6zHKZDklkHWHvNdDooSJ2XQdB04t89/1O/w1cDnyilFU="
SECRET = "d7674280e785bfe742b0062fd2562a22"

FQDN = "https://digit-num-recognition.herokuapp.com"


line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(SECRET)

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
    num = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ''] 
    message_content = line_bot_api.get_message_content(event.message.id)
    # 取得した画像ファイル
    with open("static/"+event.message.id+".jpg", "wb") as f:
        f.write(message_content.content)
    
    img = Image.open("static/"+event.message.id+".jpg")
    img_resize = img.resize((400, 100))
    img_resize.crop((0, 0, 100, 100)).save("static/"+event.message.id+"-test.jpg", quality=95)
    img = image.load_img("static/"+event.message.id+"-test.jpg", grayscale=False, target_size=(28, 28))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = x / 255.0
    model = load_model('color_model.h5')
    result_predict = model.predict_classes(x)
    n = num[result_predict[0]]
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=n))


if __name__ == "__main__":
    app.run()
