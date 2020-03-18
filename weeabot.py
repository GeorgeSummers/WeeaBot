import mal
from vk_config import vk_token,group_id
import rss
import os
import requests
import pyquery
import json   
from datetime import datetime
from threading import Timer, Thread
import random
from vk_api import VkApi, VkUpload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

HinoCount = 10

def send_msg(chat_id,msg,att=''):
    random_id = round(random.random() * 10 ** 9)
    vk.messages.send( 
                random_id=random_id,
                chat_id=chat_id,
                message=msg,
                attachment=att
                )

def private_msg(peer_id,msg,att=''):
    vk.messages.send(
                peer_id=peer_id,
                message=msg,
                attachment=att
            )

def get_user_data(uid):
    return vk.users.get(user_ids = int(uid))

def roll_ptw(usr):
    lst= mal.get_user(usr,"animelist","plantowatch")['anime']
    newList = []
    for i in lst:
        if i['airing_status']==2:
            newList.append(i)
            continue
    return random.choice(newList)


vk_session = VkApi(token=vk_token)
longpoll = VkBotLongPoll(vk_session, group_id)

vk = vk_session.get_api()
upload=VkUpload(vk_session)

print('Running WeeaBot...\n')
send_msg(3,"皆のために僕は頑張ります!\n",'photo-117602761_457239211')

for event in longpoll.listen():
    print(event)
    print('\n')
    if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat:
        
        if event.obj.from_id == 38705372 and HinoCount == 10:
            send_msg(int(event.chat_id),"МАЛ сам себя не пофиксит.","photo-117602761_457239139")
            HinoCount-=1
            if HinoCount == 0:
                HinoCount = 10

        if event.obj.text[:5].lower() == '/bind':
            print('Binding MAL')
            usr =  event.obj.text[6:]
            try:
                with open("binds.json", 'r+') as file:

                    data = json.load(file)
                    data[str(event.obj.from_id)]= usr
                    print(data)
                    file.seek(0) 
                    json.dump(data,file)
                    send_msg(int(event.chat_id),"Ваш MAL привязан\n" + mal.url_mal + usr)
                    continue
            except:
                with open("binds.json", 'w') as f:
                    json.dump({str(event.obj.from_id) : usr},f)

        if event.obj.text.lower() == "/nakama":
            print('Getting nakamas')
            strn=''
            with open("bindings.json", 'r') as file:
                data = json.load(file)
                for key,val in data.items():
                    user=get_user_data(key)
                    strn+=f"{user[0]['first_name']} {user[0]['last_name']} - {mal.url_mal + val}\n"
                send_msg(int(event.chat_id),"Ссылки на ребят:\n%s" % strn)

        if event.obj.text.lower() == "/mustw":
            send_msg(int(event.chat_id),"Ссылка на MUSTWATCH список:",'https://docs.google.com/document/d/1aOsjs9C8mqcOasVvgqwKkzGDTfGHvAKgNWN0x--H6lk/edit')

        if event.obj.text[:5].lower() == "/roll":
            data={}
            with open("binds.json", 'r') as file:
                data = json.load(file)
            res = roll_ptw(data[str(event.obj.from_id)])
            title= res['title']
            stype=res['type']
            eps=res['total_episodes']
            url=res['url']
            with requests.Session() as session:
                image = session.get(res['image_url'].split('?')[0], stream=True)
                att=upload.photo_messages(photos=image.raw)[0]
                send_msg(int(event.chat_id),f'{title}\n{stype}, {eps} Episodes\n{url}','photo{}_{}'.format(att['owner_id'], att['id'])) 

        if event.obj.text == "/help":
            message="""Добро пожловать в наш уютный чатик!
Список команд:
/help - помощь.
/bind <MAL-username> - привязка MAL-аккаунта к беседе по имени профиля.
/nakama - Получить список МАЛа собеседников.
/mustw - (пока что) ссылка на MUSTWATCH список
/roll - Рандомный тайтл из Вашего ПТВ
/rss <channel> [filter] - СКОРО!
"""
            send_msg(int(event.chat_id),message)
