from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage   # 載入 TextSendMessage 模組
import json

app = Flask(__name__)

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)
    json_data = json.loads(body)
    print(json_data)
    try:
        line_bot_api = LineBotApi('Hov5TnfbE/8e6kbS2XKYxngqlD5EjNLi8G6+RBM980y8hRed183iRdMXnJB8w6CDarw358rcHM4UQNTBPI8WLsivSZfQ1g2xkakLCk9DU1fL10rN8JJuBoX1CmhuQpukv4LewLrxMoV3ly2eXJsSPQdB04t89/1O/w1cDnyilFU=')
        handler = WebhookHandler('e5319c4054ab67f56fa2625b4f82e4ab')
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)
        tk = json_data['events'][0]['replyToken']         # 取得 reply token
        msg = json_data['events'][0]['message']['text']   # 取得使用者發送的訊息
        text_message = TextSendMessage(text=msg)          # 設定回傳同樣的訊息
        line_bot_api.reply_message(tk,text_message)       # 回傳訊息
    except:
        print('error')
    return 'OK'

if __name__ == "__main__":
    app.run()
    
