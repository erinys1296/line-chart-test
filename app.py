from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import random
import os

app = Flask(__name__)

PLAYING = False

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
    try:
        temp = PLAYING 
    except:
        PLAYING = False
    
    if event.message.text == '開始' and PLAYING == False:
        answer = random.randint(1,100)
        message = TextSendMessage(text="請從1到100中猜個數字 " + str(answer) +str(PLAYING))
        
        PLAYING = True
        line_bot_api.reply_message(event.reply_token, message)
    elif PLAYING == True:
        try:
            guass = int(event.message.text)
            if guass == answer:
                UserName = event.source.display_name
                username = line_bot_api.get_profile(UserName)
                line_bot_api.reply_message(event.reply_token, '恭喜' + username + '猜對啦!')
                PLAYING = False
            else:
                line_bot_api.reply_message(event.reply_token, '猜錯囉!請繼續!')
        except:
            line_bot_api.reply_message(event.reply_token, '請輸入數字')
        
    else:
        message = TextSendMessage(text=event.message.text+str(PLAYING))
        line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    PLAYING = False
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
