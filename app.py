import numpy as np

from flask import Flask, request, abort

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage)

from keras.models import load_model
from keras.preprocessing import image

import cv2 



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
    message_content = line_bot_api.get_message_content(event.message.id)
    # 取得した画像ファイル
    with open("static/"+event.message.id+".jpg", "wb") as f:
        f.write(message_content.content)

        test_url = "./static/"+event.message.id+".jpg"


        img = cv2.imread(test_url) # ここに数字画像認識をしたい画像を入れます。事前に4等分を考慮して撮影した画像を利用
        img = cv2.resize(img, (400,  100)) # サイズが調整されていない画像を入れた場合のエラー予防
        #img = cv2.resize(img, (800,  200))  # 画像を横の幅800・高さ200ピクセルにリサイズするプログラム例


        # 画像のトリミング [y1:y2, x1:x2]  （img = cv2.resize(img, (400,  100)) を使った場合のプログラム例

        data1 = img[0:100, 0:100]     #yの範囲（縦）が0〜100・xの範囲（横）が0〜100までをトリミング
        data2 = img[0:100, 100:200] #yの範囲（縦）が0〜100・xの範囲（横）が100〜200までをトリミング
        data3 = img[0:100, 200:300] #yの範囲（縦）が0〜100・xの範囲（横）が200〜300までをトリミング
        data4 = img[0:100, 300:400] #yの範囲（縦）が0〜100・xの範囲（横）が300〜400までをトリミング



        img = image.load_img(test_url, target_size=(150, 150))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = x / 255.0
        # モデルのロード
        model = load_model('dog_cat.h5')
        result_predict = model.predict(x)

        if result_predict < 0.5:
            text = "This is cat"
        if result_predict >= 0.5:
            text = "This is dog"

        #line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=FQDN+"/static/"+event.message.id+".jpg",preview_image_url=FQDN+"/static/"+event.message.id+".jpg"))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text))

if __name__ == "__main__":
    app.run()
