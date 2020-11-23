from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from linebot.models.events import *
from linebot.models.template import *
import json

#Using the Medium_Crawler to build the chatbot
import MediumCrawler

secretFileContentJson=json.load(open("line_secret_key",'r',encoding="utf-8"))
print(secretFileContentJson.get("channel_access_token"))
print(secretFileContentJson.get("secret_key"))
print(secretFileContentJson.get("self_user_id"))

app = Flask(__name__)

line_bot_api = LineBotApi('XXX')
handler = WebhookHandler('XXX')


@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

#Richmenu, create rich menu as body
body =""" {
    "size": {
        "width": 2500,
        "height": 843
    },
    "selected": true,
    "name": "Rich Menu 1",
    "chatBarText": "RichMenu",
    "areas": [
        {
            "bounds": {
                "x": 199,
                "y": 69,
                "width": 527,
                "height": 550
            },
            "action": {
                "type": "postback",
                "text": "::推薦選讀",
                "data": "推薦選讀"
            }
        },
        {
            "bounds": {
                "x": 982,
                "y": 69,
                "width": 527,
                "height": 543
            },
            "action": {
                "type": "postback",
                "text": "::尋找知識",
                "data": "尋找知識"
            }
        },
        {
            "bounds": {
                "x": 1765,
                "y": 69,
                "width": 527,
                "height": 556
            },
            "action": {
                "type": "postback",
                "text": "::專業設定",
                "data": "專業設定"
            }
        }
    ]
}"""

menuJson=json.loads(body)
lineRichMenuId = line_bot_api.create_rich_menu(rich_menu=RichMenu.new_from_json_dict(menuJson))
print(lineRichMenuId)
# Retrieve the richmenu from https://drive.google.com/file/d/1-ZdJ6Js_L4wNACH4Gq8Tiw9T4qQPKRa3/view?usp=sharing
uploadImageFile=open("richmenu.png", 'rb')
setImageResponse = line_bot_api.set_rich_menu_image(lineRichMenuId,'image/jpeg',uploadImageFile)
linkResult = line_bot_api.link_rich_menu_to_user(secretFileContentJson["self_user_id"], lineRichMenuId)

#Global varible to record user profile

perference = "程式 開發"
ignore = ""
function = "recommend"
import random
random.seed(a=None, version=2)

#def get_user_record(user_profile):
#    command = database.cursor()
#    command.execute(f"SELECT `readed` FROM `user` WHERE `line_id` = '{user_profile.user_id}'")
#    ignore = command.fetchall()
#    ignore = ignore[0]
#    return ignore

#for replying with data
@handler.add(PostbackEvent)
def handle_postback_event(event):
    global perference
    global function
    global ignore
    user_profile = line_bot_api.get_profile(event.source.user_id)

    #ignore = get_user_record(user_profile)
    postback_data = event.postback.data
    #製作QuickReply先做按鍵再作QuickReply夾帶SendMessage內，送回給用戶。
    #qrb1=QuickReplyButton(action=MessageAction(label="今天到這裡",text="下課"))
    #qrb2=QuickReplyButton(action=MessageAction(label="就到這裡", text="停課"))
    #quick_reply_list=QuickReply([qrb1,qrb2])

    if postback_data == "研發工程":
        perference = "開發"
    elif postback_data == "設計互動":
        perference = "設計"
    elif postback_data == "產品企劃":
        perference = "產品"
    elif postback_data == "市場行銷":
        perference = "行銷"
    elif postback_data == "專業設定":
        line_bot_api.reply_message(event.reply_token, setting_message_list)
    elif postback_data == "推薦選讀":
        function = "recommend"
        print(ignore)
        new_list = MediumCrawler.Crawler(perference, 3, ignore)
        recommend_list = TemplateSendMessage(
            alt_text='Recommanded Articles', template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url=f"{new_list[0][7]}",
                        title=f"{new_list[0][2][:40]}",
                        text=f"{new_list[0][3][:60]}",
                        actions=[
                            URIAction(
                                label='打開文章',
                                uri=f'{new_list[0][-3]}'
                            ),
                            PostbackAction(
                                label='標示已讀',
                                display_text='已過讀此篇，下次不會出現囉！',
                                data='已讀文章1'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{new_list[1][7]}",
                        title=f"{new_list[1][2][:40]}",
                        text=f"{new_list[1][3][:60]}",
                        actions=[
                            URIAction(
                                label='打開文章',
                                uri=f'{new_list[1][-3]}'
                            ),
                            PostbackAction(
                                label='標示已讀',
                                display_text='已過讀此篇，下次不會出現囉！',
                                data='已讀文章2'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{new_list[2][7]}",
                        title=f"{new_list[2][2][:40]}",
                        text=f"{new_list[2][3][:60]}",
                        actions=[
                            URIAction(
                                label='打開文章',
                                uri=f'{new_list[2][-3]}'
                            ),
                            PostbackAction(
                                label='標示已讀',
                                display_text='已過讀此篇，下次不會出現囉！',
                                data='已讀文章3'
                            )
                        ]
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,recommend_list)
    elif postback_data == "尋找知識":
        line_bot_api.reply_message(event.reply_token, finding_message)
    elif postback_data == "已讀文章1":
        if function == "recommend":
            new_list = MediumCrawler.Crawler(perference, 3, ignore)
            ignore = ignore + f",{new_list[0][0]},{new_list[1][0]},{new_list[2][0]}"
            print(ignore)
            line_bot_api.reply_message(event.reply_token, recording_message)
        elif function != "recommend":
            customized_list = MediumCrawler.Crawler(function, 3, ignore)
            ignore = ignore + f",{customized_list[0][0]},{customized_list[1][0]},{customized_list[2][0]}"
            print(ignore)
            line_bot_api.reply_message(event.reply_token, recording_message)

    elif postback_data == "已讀文章2":
        if function == "recommend":
            new_list = MediumCrawler.Crawler(perference, 3, ignore)
            ignore = ignore + f",{new_list[0][0]},{new_list[1][0]},{new_list[2][0]}"
            line_bot_api.reply_message(event.reply_token, recording_message)
        elif function != "recommend":
            customized_list = MediumCrawler.Crawler(function, 3, ignore)
            ignore = ignore + f",{customized_list[0][0]},{customized_list[1][0]},{customized_list[2][0]}"
            line_bot_api.reply_message(event.reply_token, recording_message)
    elif postback_data == "已讀文章3":
        if function == "recommend":
            new_list = MediumCrawler.Crawler(perference, 3, ignore)
            ignore = ignore + f",{new_list[0][0]},{new_list[1][0]},{new_list[2][0]}"
            line_bot_api.reply_message(event.reply_token, recording_message)
        elif function != "recommend":
            customized_list = MediumCrawler.Crawler(function, 3, ignore)
            ignore = ignore + f",{customized_list[0][0]},{customized_list[1][0]},{customized_list[2][0]}"
            line_bot_api.reply_message(event.reply_token, recording_message)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global ignore
    global function
    if event.message.text.find('::') == 0:
        pass
    else:
        user_keyword = event.message.text
        function = user_keyword
        print(ignore)
        customized_list = MediumCrawler.Crawler(user_keyword, 3, ignore)
        customized_recommend_list = TemplateSendMessage(
            alt_text='Customized Recommanded Articles', template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url=f"{customized_list[0][7]}",
                        title=f"{customized_list[0][2][:40]}",
                        text=f"{customized_list[0][3][:60]}",
                        actions=[
                            URIAction(
                                label='打開文章',
                                uri=f'{customized_list[0][-3]}'
                            ),
                            PostbackAction(
                                label='標示已讀',
                                display_text='已過讀此篇，下次不會出現囉！',
                                data='已讀文章1'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{customized_list[1][7]}",
                        title=f"{customized_list[1][2][:40]}",
                        text=f"{customized_list[1][3][:60]}",
                        actions=[
                            URIAction(
                                label='打開文章',
                                uri=f'{customized_list[1][-3]}'
                            ),
                            PostbackAction(
                                label='標示已讀',
                                display_text='已過讀此篇，下次不會出現囉！',
                                data='已讀文章2'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=f"{customized_list[2][7]}",
                        title=f"{customized_list[2][2][:40]}",
                        text=f"{customized_list[2][3][:60]}",
                        actions=[
                            URIAction(
                                label='打開文章',
                                uri=f'{customized_list[2][-3]}'
                            ),
                            PostbackAction(
                                label='標示已讀',
                                display_text='已過讀此篇，下次不會出現囉！',
                                data='已讀文章3'
                            )
                        ]
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, customized_recommend_list)

# for following
@handler.add (FollowEvent)
def reply_set_user_profile(event):
    user_profile = line_bot_api.get_profile(event.source.user_id)
    user_id = user_profile.user_id
    name = user_profile.display_name
    language = user_profile.language
    picture = user_profile.picture_url
    line_bot_api.reply_message(event.reply_token, welcome_message_list)
    linkResult = line_bot_api.link_rich_menu_to_user(user_id, lineRichMenuId)

welcome_message_list = [

    TextSendMessage(text="歡迎使用 Blog樂。 一個依照您的專業與興趣推薦部落格文章的微學習聊天機器人。開始之前我們需要蒐集您的偏好來推薦文章！"),

    TemplateSendMessage(alt_text='Set Profession', template=ButtonsTemplate(
        thumbnail_image_url='https://topics.amcham.com.tw/wp-content/uploads/2019/09/09_2019_topics-president-view-nextgen-leaders-program.jpg',
        text='首先請告訴我們您感興趣的專業領域是甚麼吧！',
        actions=[
            PostbackAction(label='研發工程',text="::好的！您的個人資料已更新！",data='研發工程'),
            PostbackAction(label='設計互動',text="::好的！您的個人資料已更新！",data='設計互動'),
            PostbackAction(label='產品企劃',text="::好的！您的個人資料已更新！",data='產品企劃'),
            PostbackAction(label='市場行銷',text="::好的！您的個人資料已更新！",data='市場行銷'),
        ]))
]

finding_message = [TextSendMessage( text="只要在聊天畫面輸入您想找的知識，Blog樂 就會為您搜尋囉")]

recording_message = [TextSendMessage(text="這篇文章已被標為已讀。")]

setting_message_list = [
    TemplateSendMessage(alt_text='Buttons template', template=ButtonsTemplate(
        thumbnail_image_url='https://topics.amcham.com.tw/wp-content/uploads/2019/09/09_2019_topics-president-view-nextgen-leaders-program.jpg',
        text='請告訴我們您感興趣的專業領域是甚麼吧！',
        actions=[
            PostbackAction(label='研發工程',text="::好的！您的個人資料已更新！",data='研發工程'),
            PostbackAction(label='設計互動',text="::好的！您的個人資料已更新！",data='設計互動'),
            PostbackAction(label='產品企劃',text="::好的！您的個人資料已更新！",data='產品企劃'),
            PostbackAction(label='市場行銷',text="::好的！您的個人資料已更新！",data='市場行銷'),
        ]))
]
import os
if __name__ == "__main__":
    app.run()
    #app.run(host='0.0.0.0',port=os.environ['PORT'])
