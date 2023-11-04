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
    if event.source.type == 'group':
        dataid = event.source.group_id
    else:
        
        dataid = username.user_id
    try: 
        test = fdb.get('/'+dataid,'start')
    except:
        fdb.put('/'+dataid,'start',0)
    if event.message.text == '開始':
        answer = random.randint(1,100)
        message = TextSendMessage(text="請從1到100中猜個數字 " + str(answer))
        line_bot_api.reply_message(event.reply_token, message)
        counter = 0
        fdb.put('/'+dataid,'start',1)
        fdb.put('/'+dataid,'min',1)
        fdb.put('/'+dataid,'max',100)
        fdb.put('/'+dataid,'answer',answer)
        
    elif fdb.get('/'+dataid,'start') == 1:
        min = fdb.get('/'+dataid,'min')
        max = fdb.get('/'+dataid,'max')
        if int(event.message.text) == fdb.get('/'+dataid,'answer'):
            
            message = TextSendMessage(text= username.display_name + " 答對了！好厲害！")
            line_bot_api.reply_message(event.reply_token, message)
            fdb.put('/'+dataid,'start',0)
        elif int(event.message.text) > fdb.get('/'+dataid,'answer'):
            fdb.put('/'+dataid,'max',int(event.message.text) )
            max = int(event.message.text) 
            message = TextSendMessage(text= "請從{}到{}中猜個數字".format(min,max) )
            line_bot_api.reply_message(event.reply_token, message)
        else:
            fdb.put('/'+dataid,'min',int(event.message.text) )
            min = int(event.message.text) 
            message = TextSendMessage(text= "請從{}到{}中猜個數字".format(min,max) )
            line_bot_api.reply_message(event.reply_token, message)
        
    else:
        UserName = event.source.user_id
        username = line_bot_api.get_profile(UserName)
        message = TextSendMessage(text= username.display_name + username.user_id)
        line_bot_api.reply_message(event.reply_token, message)
        fdb.put('/'+dataid,'test',event.message.text)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
