import os
import sys
import json
from datetime import datetime

import requests
from flask import Flask, request
from employee import *

app = Flask(__name__)

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  # someone sent us a message
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    name = get_infor(sender_id)

                    if message_text == 'Giai phap khac':
                        send_message(sender_id,"vmarketing")
                        send_quick_reply(sender_id, "vmarketing")

                    elif message_text == 'Tu van sau':
                        web_view(sender_id,"vmarketing")

                    elif message_text == 'Tu van ngay':
                        send_mes(sender_id,'Nhan vien cua chung toi se tu van cho ban ve cac giai phap cua Vmarketing.')
                    phone =""
                    mail_add =""
                    if message_text.isdigit()== True and len(message_text)==10 :
                        phone = message_text
                    if message_text.find('@vivas.vn') != -1:
                        mail_add= message_text
                    if len(phone)!= 0 and len(mail_add) != 0:
                        insert_employee(name,sender_id,phone,mail_add)

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    sender_id = messaging_event["sender"]["id"]      # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]
                    name = get_infor(sender_id)
                    if messaging_event['postback']['payload'] == "{\"type\":\"legacy_reply_to_message_action\",\"message\":\"Get Started\"}":
                        tmp = json.dumps(messaging_event['postback'])
                        ref =""
                        if tmp.find('referral') != -1:
                            ref = messaging_event['postback']['referral']['ref']
                        if ref =="employee":
                            get_infor_employee(sender_id,"Nhap SDT va email cua ban:")                          
                        elif ref !="employee":
                            send_mes(sender_id, 'Chung toi quan niem: "Dung ep doanh nghiep linh hoat theo giai phap ma phai dem den giai phap linh hoat voi doanh nghiep"')
                            send_attachment(sender_id,"vmarketing")
                            send_quick_reply(sender_id, "vmarketing")
                        
                                               
    return "ok", 200

def link_referral(sender_id,page_id):
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
    "sender":{
        "id": sender_id
    },
    "recipient":{
        "id": page_id
    },
    "timestamp":1458692752478,
    "postback":{
        "payload":"{\"type\":\"legacy_reply_to_message_action\",\"message\":\"link\"}",
        "referral": {
        "ref": "employee",
        "source": "SHORTLINK",
        "type": "OPEN_THREAD",
        }
    }
    })

def get_infor(sender_id):
    url = "https://graph.facebook.com/{0}".format(sender_id)
    payload = { 
        "fields": "name,gender",
        "access_token": os.environ["PAGE_ACCESS_TOKEN"] 
        }
    r = requests.get(url,params = payload)
    result = json.loads(r.text)
    return result['name']

#ham nhap TT nhan vien
def get_infor_employee(recipient_id, message_text):

    log("get infor to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    } 
    headers = {
        "Content-Type": "application/json",
        "charset": "utf-8"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": { 
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v4.0/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_mes(recipient_id, message_text):

    log("sending mes to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    } 
    headers = {
        "Content-Type": "application/json",
        "charset": "utf-8"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": { 
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v4.0/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

#ham gui tin nhan
def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment":{
        "type":"template",
        "payload":{
        "template_type":"generic",
        "elements":[
           {
            "title":"Vmarketing",
            "image_url":"https://imgur.com/9lx0cNv.png",
            "buttons":[
                {
                    "type": "web_url",
                    "url": "https://solutions.vmarketing.vn/loyalty-program/",
                    "title":"Loyalty Programs",
                    "webview_height_ratio": "tall",
                    "messenger_extensions": True,
                },
                {
                    "type": "web_url",
                    "url": "https://cloudcall.vmarketing.vn/cloudcall-tong-dai-doanh-nghiep-ip-pbx/",
                    "title":"Cloud Call",
                    "webview_height_ratio": "tall",
                    "messenger_extensions": True,
                }

                ]   
          }
        ]
      }
    }
        }
    })
    r = requests.post("https://graph.facebook.com/v4.0/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

#ham gui hinh anh va nut
def send_attachment(recipient_id,message_text):
    log("sending attachment to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment":{
        "type":"template",
        "payload":{
        "template_type":"generic",
        "elements":[
           {
            "title":"Vmarketing",
            "image_url":"https://imgur.com/9lx0cNv.png",
            "buttons":[
                {
                    "type": "web_url",
                    "url": "https://solutions.vmarketing.vn/chatbots-communication/",
                    "title":"Chatbot Marketing",
                    "webview_height_ratio": "tall",
                    "messenger_extensions": True,
                },
                {
                    "type": "web_url",
                    "url": "https://solutions.vmarketing.vn/mobile-marketing-solutions-giai-phap-tich-hop/",
                    "title":"Mobile Marketing",
                    "webview_height_ratio": "tall",
                    "messenger_extensions": True,
                },
                {
                    "type": "web_url",
                    "url": "https://solutions.vmarketing.vn/o2o-solutions/",
                    "title":"Online to Offline",
                    "webview_height_ratio": "tall",
                    "messenger_extensions": True,
                }
             
                ]   
          }
        ]
      }
    }
        }
    })
    r = requests.post("https://graph.facebook.com/v4.0/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


#ham cau tra loi nhanh
def send_quick_reply(recipient_id,message_text):
    log("sending quick reply to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({ 
         "recipient": {
            "id": recipient_id
        },
        "messaging_type": "RESPONSE",
        "message":{
            "text": "Ban co can them thong tin gi ve Vmarketing khong nhi?",
            "quick_replies":[
            {
                "content_type":"text",
                "title": 'Giai phap khac',
                "payload": "{\"type\":\"legacy_reply_to_message_action\",\"message\":\"giai phap\"}"
                
            },
            {
                "content_type":"text",
                "title":'Tu van ngay',
                "payload": "{\"type\":\"legacy_reply_to_message_action\",\"message\":\"chat\"}"
                
            },
            {
                "content_type":"text",
                "title": 'Tu van sau',
                "payload": "{\"type\":\"legacy_reply_to_message_action\",\"message\":\"tu van\"}"
                
            }
            ]
        }
    })
    r = requests.post("https://graph.facebook.com/v4.0/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

#de lai thong tin tu van -> hien thi webview
def web_view(recipient_id,message_text):
    log("sending web view to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({ 
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment":{
        "type":"template",
        "payload":{
        "template_type":"generic",
        "elements":[
           {
            "title":"Vui long de lai thong tin lien he cua ban de chung toi tu van nhe!",
            "buttons":[
                {
                    "type": "web_url",
                    "url": "https://forms.gle/Y4y39b7WnLQxbAzf7",
                    "title": "Nhap thong tin",
                    "webview_height_ratio": "tall",
                    "messenger_extensions": True,
                }
            ]
           } ] 
        } }
        }

    })
    r = requests.post("https://graph.facebook.com/v4.0/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku
    try:
        if type(msg) is dict:
            msg = json.dumps(msg)
        else:
            msg = unicode(msg).format(*args, **kwargs)
        print (u"{}: {}".format(datetime.now(), msg))
    except UnicodeEncodeError:
        pass  # squash logging errors in case of non-ascii text
    sys.stdout.flush()

if __name__ == '__main__':
    app.run(debug=True)
