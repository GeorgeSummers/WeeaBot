# coding=utf8

import logging
import logging.config


logging.config.fileConfig("logger.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.WARNING)

from config import *
import socket,urllib3
import mal,sauce,rss
import re
import os, sys
import requests
import base64
import json
from datetime import datetime
import time
import random
from vk_api import VkApi, VkUpload, exceptions
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id


vk_session = VkApi(token=vk_token)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, group_id, wait=60)
upload = VkUpload(vk_session)


def send_msg(event, msg, att=''):
    if event == 3:
        vk.messages.send(
            random_id=get_random_id(),    
            chat_id=3,
            message=msg,
            attachment=att
        )
    elif event.from_chat:
        print(f'replying to {event.chat_id}')
        vk.messages.send(
            random_id=get_random_id(),
            chat_id=event.chat_id,
            message=msg,
            attachment=att,         
        )
    elif event.from_user:
        print(f'replying to {event.obj.from_id}')
        vk.messages.send(
            random_id=get_random_id(),
            user_id=event.obj.from_id,
            message=msg,
            attachment=att,
        )
def private_msg(uid,msg, att=''):
    vk.messages.send(
            random_id=get_random_id(),
            user_id=uid,
            message=msg,
            attachment=att
        )

def get_user_data(uid):
    return vk.users.get(user_ids=int(uid))

def bind(event):
    usr = event.obj.text[6:]
    with open("bindings.json", 'r+') as file:
        data = json.load(file)
        data[str(event.obj.from_id)] = usr
        print(data)
        file.seek(0)
        json.dump(data, file)
        send_msg(event,
                    "Ваш MAL привязан\n" + mal.url_mal + usr)

def get_nakamas(event):
    strn = ''
    with open("bindings.json", 'r') as file:
        data = json.load(file)
        for key, val in data.items():
            user = get_user_data(key)
            strn += f"{user[0]['first_name']} {user[0]['last_name']} - {mal.url_mal + val}\n"
        send_msg(event,
                    "Ссылки на ребят:\n%s" % strn)

def roll(event):
    data = {}
    logger.warning('Rolling')
    with open("bindings.json", 'r') as file:
        data = json.load(file)
        mtext = re.sub('\[[^()]*\] ','',event.obj.text.lower())
    if mtext == '/roll':
        res = mal.roll(data[str(event.obj.from_id)])
    else:
        res = mal.roll(data[str(event.obj.from_id)],mtext.split(' ')[1])
    if not res ==[]:
        title = res['title']
        stype = res['type']
        eps = res['total_episodes']
        url = res['url']
        with requests.Session() as session:
            image = session.get(
                res['image_url'].split('?')[0], stream=True)
            att = upload.photo_messages(photos=image.raw)[0]
            send_msg(event, f'{title}\n{stype}, {eps} Episodes\n{url}', 'photo{}_{}'.format(
                att['owner_id'], att['id']))
    else:
        send_msg(event,'Ваш список пуст!')

def derangement(keys):
    if len(keys) == 1:
        raise ValueError('No derangement is possible')

    new_keys = list(keys)

    while any(x == y for x, y in zip(keys, new_keys)):
        random.shuffle(new_keys)

    return new_keys

def shuffle_dict(d):
    return { x: d[y] for x, y in zip(d, derangement(d)) }


def main():
    global vk_session,vk,longpoll,upload

    #send_msg(3, "Minna no tame ni boku wa ganbarimasu!\n", 'photo-117602761_457239211')
    vityaCount = 10
    F=True
    last_oyasumi = 0.0
    while True:
        try:
            vk_session = VkApi(token=vk_token)
            vk = vk_session.get_api()
            longpoll = VkBotLongPoll(vk_session, group_id, wait=60)
            upload = VkUpload(vk_session)
            print(f'\n{datetime.now()}    Running WeeaBot...\n')
            for event in longpoll.listen(): 
                logger.info(event.type if not event.type == VkBotEventType.MESSAGE_NEW else f'{event.type} \nfrom {list(get_user_data(event.obj.from_id)[0].values())[:3]}')
                if event.type == VkBotEventType.MESSAGE_NEW:


#                    if not event.obj.attachments == []:
#                        if event.obj.attachments[0]['type'] =='audio_message':
#                            with requests.Session() as session:
#                                msg = session.get(event.obj.attachments[0]['audio_message']['link_mp3'], stream=True)
#                            resp = translator.translate(msg)
#                           send_msg(event,resp)
                        
                    if event.obj.from_id == 255017427: 
                        if vityaCount == 100:
                            send_msg(
                                event, "МАЛ сам себя не заполнит.", "photo-117602761_457239286")
                        else:
                            if vityaCount == 0:
                                vityaCount = 11
                        vityaCount -= 1

                    if event.obj.text[:5].lower() == '/bind':
                        print(f'{datetime.now()} Binding MAL')
                        bind(event)

                    if event.obj.text.lower() == "/kiseki": 
                        send_msg(event,"Kiseki dato?!",'photo-117602761_457239368')
                        
                    if re.sub('\[[^()]*\] ','',event.obj.text.lower())  == "/nakama":
                        print(f'{datetime.now()} Getting nakamas')
                        get_nakamas(event)

                    if event.obj.text.lower() == "/mustw":
                        send_msg(event, "Ссылка на MUSTWATCH список:",
                                 'https://docs.google.com/document/d/1aOsjs9C8mqcOasVvgqwKkzGDTfGHvAKgNWN0x--H6lk/edit')

                    if re.sub('\[[^()]*\] ','',event.obj.text.lower())[:5] == "/roll":
                        print(f"{str(datetime.now())} Rolling random title...")
                        roll(event)

                    if event.obj.text[:7].lower() == '/setrss':
                        if not event.chat_id == 3:
                            print(f"{str(datetime.now())} Setting RSS...")
                            args=event.obj.text.split(' ')[1:]
                            feeds =[]
                            subs=[] 
                            with open('datrss.csv','r') as file:
                                for row in file:
                                    feeds.append(row.split()[0])
                                for word in args:
                                    arg = [i for i in feeds if word in i]
                                    subs.append(arg[0])
                            with open("bindings.json", 'r') as file:
                                data = json.load(file)
                            res = mal.get_ongoing(data[str(event.obj.from_id)])
                            with open('subrss.json', 'r+') as file:
                                lst = json.load(file)
                                lst[str(event.obj.from_id)] = (res, subs)
                                file.seek(0)
                                json.dump(lst, file)
                                file.truncate()
                            msg = "Список Ваших онгоингов получен успешно!"
                            send_msg(event, msg)
                        else:
                            send_msg(
                                event, "Для подписки на рассылку отправьте команду в ЛС!")
                    
                    if event.obj.text[:7].lower() == '/seerss':
                        print(f"{datetime.now()} setting RSS titles...")
                        with open('subrss.json','r') as file:
                            data = json.load(file)
                            msg='Вы подписаны на:\n'
                            for title in data[str(event.obj.from_id)][1]:
                                msg+=f'{title}\n'
                            send_msg(event,msg)

                    if event.obj.text[:7].lower() == '/updrss':
                        if not event.chat_id == 3:
                            query=event.obj.text.split(' ')
                            try:
                                rss.upd_data(query[1],event.obj.from_id,query[2:])
                                send_msg(event, "Список онгоингов успешно обновлен!")
                            except:
                                send_msg(event, "Произошла ошибка! Проверьте правильность введённых данных.")
                        else:
                            send_msg(
                                event, "Для подписки на рассылку отправьте команду в ЛС!")
                   
                    if event.obj.text[:4].lower() == '/rss': #feck
                        query = event.obj.text.split(' ')
                        if query[1] == 'new':
                            title = rss.get_feed(query[2])
                            send_msg(event,f'Канал {title} успешно добвлен!')
                        elif query[2] == 'sub':
                            rss.upd_data(query[2],event.obj.from_id,query[2])
                            send_msg(event,'Теперь вы подписаны на данный канал!')
                        elif query[2] == 'unsub':
                            rss.upd_data(query[2],event.obj.from_id,query[2])
                            send_msg(event,'Вы были отписаны от рассылок с канала!')

                    if event.obj.text[:6].lower() == '/sauce':
                        if not event.obj['attachments'] == []:
                            print(f'{datetime.now()} Sending sauce...')
                            with requests.Session() as session:
                                image = session.get(
                                    event.obj['attachments'][0]['photo']['sizes'][len(event.obj['attachments'][0]['photo']['sizes'])-1]['url'], stream=True)
                                response = sauce.get_sauce(base64.encodebytes(image.content))
                                title = response['title_native']
                                romanji=response['title_romaji']
                                episode=response['episode']
                                _,url,img = mal.search(romanji)
                                att = upload.photo_messages(photos=img)[0]
                                send_msg(event,f'Сурс скриншота :\n{title} || {romanji}\nEp. - {episode}\n{url}','photo{}_{}'.format(
                                    att['owner_id'], att['id']))
                        else: send_msg(event,'Вы скриншот забыли!')

                    if re.sub('\[[^()]*\] ','',event.obj.text.lower()) == "/rules":
                        print(f"{str(datetime.now())} print rules")
                        send_msg(event,
                    """Правила шаффла:
1. Брать тайтл, который ты сам комплитнул
2. Не брать тайтл, который есть у кого-то в дропах
3. Не брать тайтлы, в сезонах которых больше 24(26) серий
4. Можно использовать тайтл который кроме тебя комплитнул кто-то один из шаффлящих. Но не более одного

Механика шаффла:
Написать нашему боту Эльф9-чан в личку сообщение:
/shuffle *вставить ссылку или название тайтла*
После этого ты участвуешь в шаффле!""")

                    if re.sub('\[[^()]*\] ','',event.obj.text.lower()) == "/help":
                        print(f"{str(datetime.now())} print help")
                        message = 'Добро пожловать в наш уютный чатик!\nСписок команд:\nGlobal:\n/help - помощь.\n/bind <MAL-username> - привязка MAL-аккаунта к беседе по имени профиля.\n/nakama - Получить список МАЛа собеседников.\n/shuffle - получить результат лотереи тайтлов\n/sauce - при отправке вложения пытается определить тайтл на скриншоте. Это должен быть оригинальный необрезанный скриншот с контентом.\n/mustw - (пока что) ссылка на MUSTWATCH список\n/roll - Рандомный тайтл из Вашего ПТВ\n/rss <new, sub, unsub> [arg] - редактировать список каналов\n-new <link> - добавить новый канал по ссылке\n-sub <name> - подписаться на канал\n-unsub <name> - отписаться от канала\nDirect:\n/shuffle <title> - добвить тайтл к лотерее\n/setrss  - Получить список оноингов для рассылок (только в ЛС)\n/seerss - посмотреть список тайтлов для рассылки\n'
                        send_msg(event, message)

                    if event.obj.text == 'F' and event.chat_id == 3:
                        if F:
                            send_msg(event,"F",'photo-117602761_457239232')
                            F=False
                    else: F = True

                    if any(re.compile(word,re.U).search(event.obj.text) for word in plotdict):
                        send_msg(event,"",'doc-117602761_539963442')

                    if any(re.compile(word,re.U).search(event.obj.text) for word in culturedict):
                        send_msg(event,"",'photo-117602761_457239235')

                    if any(re.compile(word,re.U).search(event.obj.text) for word in regboidict):
                        send_msg(event,"",'photo-117602761_457239261')

                    if any(re.compile(word,re.U).search(event.obj.text) for word in oyasumidict):
                        now_oyasumi = time.time()
                        print(last_oyasumi, now_oyasumi)
                        if last_oyasumi < now_oyasumi - 3 * 60:
                            send_msg(event,"",'photo-117602761_457239364')
                            last_oyasumi = now_oyasumi

                    if any(re.compile(word,re.U).search(event.obj.text) for word in discussiondict):
                        send_msg(event,"",'photo-117602761_457239367')


                    if event.obj.text[:8] == '/shuffle':
                        # TODO ПРОВЕРИЦ
                        with open('shuffle.json','r+') as file:
                            sl : dict = json.load(file)
                            if event.chat_id == 3 and event.obj.text == '/shuffle':
                                if not len(sl) < 2:
                                    print('shuffle')
                                    msg ='Результат лотереи:\n'
                                    for key, val in shuffle_dict(sl).items():
                                        ufn = get_user_data(key)[0]['first_name']
                                        uln = get_user_data(key)[0]['last_name']
                                        msg +=f'{ufn} {uln} - {val}\n'
                                    send_msg(event,msg)
                                    file.seek(0)
                                    file.truncate()
                                    json.dumps('{}')
                                else:
                                    send_msg(event,'Недостаточно участников!')
                            elif event.from_user:                         
                                vk.messages.markAsRead(peer_id=event.obj.peer_id,start_message_id=event.obj.id,group_id=group_id)
                                sl[str(event.obj.from_id)] = event.obj.text[8:]
                                file.seek(0)
                                json.dump(sl, file)
                                file.truncate()
                                
                    #admin commands
                    if event.obj.from_id == admin:
                       if event.obj.text == "/kill": 
                            private_msg(admin,"Terminating WeeaBot...")
                            rss.stop_listen()
                            sys.exit() 
                        
                       if event.obj.text== '/gorss':
                            rss.start_listen()
                            private_msg(admin, 'RSS thread started...')
                        
                       if event.obj.text== '/stoprss':
                            rss.stop_listen()
                            private_msg(admin, 'RSS thread stopped...')

        except (KeyboardInterrupt,SystemExit) as e:
            #send_msg(3,"Ima wa koko kara kaetakuarimasen…(╥﹏╥)","photo-117602761_457239215")
#            vk.messages.send(
#                random_id=get_random_id(),
#                chat_id=3,
#                message='Terminating WeeaBot...',
#                keyboard=json.dumps({"buttons":[],"one_time":True})           
#               )
            sys.exit()
        except requests.exceptions.ReadTimeout as timeout:
            print(f'\n{datetime.now()} timeout!\n')
            continue    
        except (requests.exceptions.ConnectionError,
                socket.gaierror,
                urllib3.exceptions.NewConnectionError,
                urllib3.exceptions.ProtocolError,
                exceptions.ApiError,
                TimeoutError) as cerror:
            start_time=time.time()
            print(f'{datetime.now()} {cerror}')
#           if time.time() > start_time + 30.0:
#              raise Exception('Unable to establish connection')
#           else:
            time.sleep(5)

def notify(feed,titles):
    with open('subrss.json','r') as sfile:
        subs = json.load(sfile)
        for key,val in subs.items():
            if feed in val[1]:
                msg=f'{feed} >'
                res = {k: v for d in titles for k, v in d.items()}
                for item in val[0]:
                    for tkey,tval in res.items(): 

                        if item in tkey:
                            msg+=f'\n{tkey} - {tval}'
                        else:
                            try:
                                title,_,_ = mal.search(re.sub('\[.*?\]','',tkey),{'status': 'airing'})
                                if item in title:
                                    msg+=f'\n{tkey} - {tval}'
                            except Exception as ex:
                                continue
                if not msg.split('>')[1] =='':
                    logger.info(f'sending msg to {key}')
                    private_msg(int(key),msg)

if __name__ == '__main__':
    logger.warning('logging from main')
    main()
