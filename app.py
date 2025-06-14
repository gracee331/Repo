import os
from flask import Flask, request, abort

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    TemplateMessage, ConfirmTemplate, MessageAction,
    CarouselTemplate,
    CarouselColumn,
    URIAction,
    PostbackAction
)

app = Flask(__name__)

configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
line_handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        action = event.message.text
        if action == 'confirm':
            reply = TemplateMessage(
                alt_text="這是確認視窗",
                template=ConfirmTemplate(
                    text="你喜歡史迪奇嗎？",
                    actions=[
                        MessageAction(label="是", text="你真棒!"),
                        MessageAction(label="否", text="不!你喜歡史迪奇")
                    ]
                )
            )
        elif action == 'carousel':
          carousel_template = CarouselTemplate(
              columns=[
                  CarouselColumn(
                      thumbnail_image_url='https://upload.wikimedia.org/wikipedia/zh/4/4b/Big_Hero_6_%28film%29_poster.jpg',
                      title='大英雄天團',
                      text='可愛氣球杯麵主演的日本電影',
                      actions=[
                          URIAction(label='查看詳情', uri='https://www.niusnews.com/=P312ww05'),
                          MessageAction(label="投票", text="我投杯麵一票")
                      ]
                ),
                  CarouselColumn(
                      thumbnail_image_url='https://upload.wikimedia.org/wikipedia/zh/d/d0/Snow_White_2025_poster.jpg',
                      title='白雪公主',
                      text='童話故事改編電影',
                      actions=[
                          URIAction(label='查看詳情', uri='https://meet.eslite.com/tw/tc/article/202504280001'),
                          MessageAction(label="投票", text="我投白雪公主一票")
                      ]
                )
            ]
          )
          reply = TemplateMessage(
              alt_text="這是輪播視窗",
              template=carousel_template
            )
        else:
          reply = TextMessage(text='Thanks!')

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                   reply
                ]
            )
        )

if __name__ == "__main__":
    app.run()
