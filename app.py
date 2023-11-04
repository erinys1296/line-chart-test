from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import random
import os
import openai
from firebase import firebase
url = 'https://line-notify-a56be-default-rtdb.firebaseio.com/'
fdb = firebase.FirebaseApplication(url, None)    # 初始化，第二個參數作用在負責使用者登入資訊，通常設定為 None

app = Flask(__name__)


line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    UserName = event.source.user_id
    username = line_bot_api.get_profile(UserName)
    try: 
        test = fdb.get('/'+username.user_id,'start')
    except:
        fdb.put('/'+username.user_id,'start',0)
    if event.message.text == '開始':
        answer = random.randint(1,100)
        message = TextSendMessage(text="請從1到100中猜個數字 " + str(answer))
        line_bot_api.reply_message(event.reply_token, message)
        counter = 0
        fdb.put('/'+username.user_id,'start',1)
        fdb.put('/'+username.user_id,'answer',answer)
        
    elif fdb.get('/'+username.user_id,'start') == 1:
        if int(event.message.text) == fdb.get('/'+username.user_id,'answer'):
            message = TextSendMessage(text= "答對了！好厲害！")
            line_bot_api.reply_message(event.reply_token, message)
            fdb.put('/'+username.user_id,'start',0)
        elif int(event.message.text) > afdb.get('/'+username.user_id,'answer'):
            message = TextSendMessage(text= "太小了喔，再猜一次")
            line_bot_api.reply_message(event.reply_token, message)
        else:
            message = TextSendMessage(text= "太大了喔，再猜一次")
            line_bot_api.reply_message(event.reply_token, message)
        
    else:
        UserName = event.source.user_id
        username = line_bot_api.get_profile(UserName)
        message = TextSendMessage(text= username.display_name + username.user_id)
        line_bot_api.reply_message(event.reply_token, message)
        fdb.put('/'+username.user_id,'test',event.message.text)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
