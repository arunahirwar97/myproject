from logging import exception
from flask import Flask, request
from waapis import create_group_chatapi 
from flask_pymongo import PyMongo
from pymongo.mongo_client import MongoClient
import mysec
import waapis
import requests
import json
app = Flask(__name__)



# Database config
app.config["MONGO_URI"] = mysec.MONGO_URI
mongo = PyMongo(app)
client = MongoClient(mysec.MONGO_URI)

db = client['dynamic_group_chatbot_dev']
groups = db.groups   


def getGroupChatID(groupname):
    chatid = groups.find_one({'groupname' : groupname})
    if(chatid is not None):
        return chatid['chatId']
    url = f"{mysec.API_URL}dialogs?token={mysec.TOKEN}"
    headers = {'Content-type': 'application/json'}
    resp = requests.get(url=url, headers=headers)
    groupsdata = {}
    alldata = resp.json()
    for item in (alldata['dialogs']):
        if(item['metadata']['isGroup'] and item['name'] == groupname):
            return item['id']
    return None





msg1 = "Hi \n\nThank you very much for responding to our ad as it is our duty at Nanopulse to provide top-quality service to people in need for a tattoo removal procedure, like you. \n\nWe know that having a tattoo can be something of a life-long commitment when you decide to have one, but it doesn't have to be that way when the tattoo isn't what you expected when it was finished.\n\nBefore we proceed, may I know what is the size of your tattoo?\n\nPlease choose below options\n\nReply 1 for Small Size \nReply 2 for Medium Size \nReply 3 for Large size"


msg2 = "Thank you! Can you also send one clear picture of the tattoo?"

msg3 = "Is your tattoo a cover-up? Please choose below options\nYes Reply 1\n No Reply 2"

msg4 = "Last question, have you done any tattoo removal before?\nYes Reply 1\nNo Reply 2"


msg5 = "Thank yo so much for all these information ! One of our staff will get back to you shortly !"

msgs = [msg2, msg3, msg4, msg5]


@app.route('/')
def index():
    return "Application is Up !!!! 2.0.0"



'''

{'messages': [{'id': 'false_120363040173984687@g.us_C960FF9BFCE6CD8CBBB62E522021A569_6593202649@c.us', 'body': 'Happy birthday @6581981427', 'fromMe': False, 'self': 0, 'isForwarded': None, 'author': '6593202649@c.us', 'time': 1651496940, 'chatId': '120363040173984687@g.us', 'messageNumber': 20185, 'type': 'chat', 'senderName': 'HamkaHasse', 'caption': None, 'quotedMsgBody': None, 'quotedMsgId': None, 'quotedMsgType': None, 'metadata': None, 'ack': None, 'chatName': '20/5 FRIDAY FLOORBALL'}], 'instanceId': '350463'}


'''


@app.route('/j', methods=['POST'])
def handleWebhook():
    try:

        print("request for webhhok")

        data = request.json
        if "messages" in data.keys():

            for msg in data['messages']:

                if(msg['fromMe']):
                    return "my msg"
                msg_text = (msg['body'])
                try:
                    msg_text = int(msg_text)
                except:
                    print("text type of reply")
                chatid = msg['chatId']
                sender = msg['author']
                sender = sender[:-5]
                group_obj = groups.find_one({'chatId' : chatid , 'chatbot' : 1})
                if group_obj is not None and (str(group_obj['customer']) == str(sender)):
                    filter = {'_id' : group_obj['_id']}
                    msg_number = group_obj['msg_sent']
                    newvalues = { "$set": { 'msg_sent': msg_number +1 } }
                    if(msg_number == 0 and(msg_text not in [1,2,3])):
                        return "Wrong Reply"

                    elif(msg_number == 2 and(msg_text not in [1,2])):
                        return "Wrong Reply"
                    elif(msg_number == 3 and(msg_text not in [1,2])):
                        return "Wrong Reply"

                    if(msg_number > 3):
                        print("Msg Number exceding")
                        return "done"
                    
                    #sending msg on group
                    msg_body = msgs[msg_number]
                    url = f"{mysec.API_URL}sendMessage?token={mysec.TOKEN}"
                    headers = {'Content-type': 'application/json'}
                    data = {
                        "body": msg_body,
                        "chatId": chatid
                    }
                    resp = requests.post(url=url, headers=headers, data=json.dumps(data))
                    groups.update_one(filter, newvalues)
                    print(resp.text)
                    return resp.text
                else:
                    
                    print("Group not exist in DB or msg from the owner")
                    return "group not exists"
        else:
            return "Out of my Scope"

    except Exception as e:
        print(e)
        return str(e)
    



@app.route('/groupcreate', methods=['POST'])
def create_group():
    request_data = request.get_json()

    phone_number = None
    group_name = ""
    if request_data:
        request_data = request.get_json()
        if ('owner' in request_data and 'customer' in request_data) and 'group_name' in request_data:
            owner = request_data["owner"].replace(",","").split()
            customer = request_data["customer"]
            # chatbot_status = request.json['bot_status']
            chatbot_status = request_data['bot_status']
            phone_list = owner.append(customer)
            phone_lst = owner
            # phone_lst.sort()

            group_name = request_data["group_name"]
            
            grps = groups.find_one({
                'phone_list': [phone_lst],
                'groupname' : group_name
                })


            if(grps is None):
                a = create_group_chatapi(phone_lst, group_name, msg1)
                data = a.json()
                newGroup = {
                    'owner': owner,
                    "customer": customer,
                    'phone_list' : phone_lst,
                    'groupname': group_name,
                    'chatId' : data['chatId'],
                    "chatbot" : chatbot_status,
                    "msg_sent": 0
                    }
                groups.insert_one(newGroup)  
                
                return data              
            

            else :
                print(grps['chatId'])
                filter = {'_id' : grps['_id']}
                newvalues = { "$set": { 'msg_sent': 0 } }
                groups.update_one(filter, newvalues)
                if(grps['chatId'] is not None):
                    chatId = grps['chatId']
                else:
                    chatId = getGroupChatID(group_name)
                
                url = f"{mysec.API_URL}sendMessage?token={mysec.TOKEN}"
                headers = {'Content-type': 'application/json'}
                data = {
                    "body": msg1,
                    "chatId": chatId
                }
                resp = requests.post(url=url, headers=headers, data=json.dumps(data))
                return resp.text
        else:
            return {"message": "Failed", "details": "phone number or group name is missing"}
        
    else:
        return {"message": "Failed", "details": "request body missing"}



if __name__ == '__main__':
    app.run()

# db_obj = {
#                 "group_name" : group_name,
#                 "phone_number" : phone_number,
#                 "chatbot" : chatbot_status,
#                 "msg_sent":0
#             }