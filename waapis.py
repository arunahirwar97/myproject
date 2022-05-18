import json
from flask import request
import requests
import mysec

API_URL = mysec.API_URL





def create_group_chatapi(phone_list, group_name, msg_txt):
    url = f"{API_URL}group?token={mysec.TOKEN}"
    
    phone_lst = phone_list
   
    headers = {'Content-type': 'application/json'}

    data = {
        "groupName": group_name,
        # "phones": ['918815312085','918815312084'],
        "phones": phone_lst,
        "messageText": (msg_txt)
    }
    print(data)
    resp = requests.post(url=url, headers=headers, data=json.dumps(data))
    print(resp)
    print(resp.text)
    return resp

def send_msg(chatid, body):
    
    chatid = request.josn['chatid']
    body = request.json['body']

    url = f"{mysec.API_URL}sendMessage?token={mysec.API_TOKEN}"
    headers = {'Content-type': 'application/json'}
    data = {
        "body": body,
        "chatId": chatid
    }
    print(data)
    resp = requests.post(url=url, headers=headers, data=json.dumps(data))
    return resp.text

if __name__ == '__main__':
    print("WhatsApp APIs")