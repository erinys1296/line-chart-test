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

    

    
    if event.message.text == '開始':
        answer = random.randint(1,100)
        message = TextSendMessage(text="請從1到100中猜個數字 " + str(answer))
        counter = 0
        while True:
            counter +=1 
            message = TextSendMessage(text= str(counter))
            line_bot_api.reply_message(event.reply_token, message)
            if counter > 5:
                break

        line_bot_api.reply_message(event.reply_token, message)
    elif event.message.text[:6].lower() == 'hi ai:':
        reply_msg = ''
        openai.api_key = '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'

        # 將第六個字元之後的訊息發送給 OpenAI
        response = openai.Completion.create(
            model='text-davinci-003',
            prompt=event.message.text[6:],
            max_tokens=256,
            temperature=0.5,
            )
        # 接收到回覆訊息後，移除換行符號
        reply_msg = response["choices"][0]["text"].replace('\n','')
        line_bot_api.reply_message(event.reply_token, reply_msg)
        
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
