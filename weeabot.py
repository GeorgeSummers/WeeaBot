# coding=utf8
from config import vk_token, group_id
import socket,urllib3
import mal
import sauce
import rss
import logging
import requests
import base64
import json
from datetime import datetime
import time
from threading import Timer, Thread
import random
from vk_api import VkApi, VkUpload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


vk_session = VkApi(token=vk_token)

vk = vk_session.get_api()


def send_msg(event, msg, att=''):
    random_id = round(random.random() * 10 ** 9)
    if event == 3:
        vk.messages.send(
            random_id=random_id,
            chat_id=3,
            message=msg,
            attachment=att
        )
    elif event.from_chat:
        print(f'replying to {event.chat_id}')
        vk.messages.send(
            random_id=random_id,
            chat_id=event.chat_id,
            message=msg,
            attachment=att
        )
    elif event.from_user:
        print(f'replying to {event.obj.from_id}')
        vk.messages.send(
            random_id=random_id,
            user_id=event.obj.from_id,
            message=msg,
            attachment=att
        )
def private_msg(uid,msg, att=''):
    random_id = round(random.random() * 10 ** 9)
    vk.messages.send(
            random_id=random_id,
            user_id=uid,
            message=msg,
            attachment=att
        )

def get_user_data(uid):
    return vk.users.get(user_ids=int(uid))


def main():
    global vk_session,vk

    #logging.basicConfig(filename='weeabot.log', level=logging.INFO)
    #send_msg(3, "皆のために僕は頑張ります!\n", 'photo-117602761_457239211')
    HinoCount = 10
    start = True
    while True:
        try:
            vk_session = VkApi(token=vk_token)
            vk = vk_session.get_api()
            longpoll = VkBotLongPoll(vk_session, group_id, wait=60)
            upload = VkUpload(vk_session)
            if start: 
                t=Thread(target=rss.listen,args=())
                t.start()
                start=False
            print(f'{datetime.now()}  Running WeeaBot...\n')

            for event in longpoll.listen():
                print(f"{datetime.now()} {event.type}")
                if event.type == VkBotEventType.MESSAGE_NEW:

                    if event.obj.from_id == 38705372: 
                        if HinoCount == 10:
                            send_msg(
                                event, "МАЛ сам себя не пофиксит.", "photo-117602761_457239139")
                        else:
                            if HinoCount == 0:
                                HinoCount = 10
                        HinoCount -= 1

                    if event.obj.text[:5].lower() == '/bind':
                        print(f'{datetime.now()} Binding MAL')
                        usr = event.obj.text[6:]
                        try:
                            with open("bindings.json", 'r+') as file:
                                data = json.load(file)
                                data[str(event.obj.from_id)] = usr
                                print(data)
                                file.seek(0)
                                json.dump(data, file)
                                send_msg(event,
                                         "Ваш MAL привязан\n" + mal.url_mal + usr)
                        except:
                            with open("bindings.json", 'w') as f:
                                json.dump({str(event.obj.from_id): usr}, f)

                    if event.obj.text.lower() == "/nakama":
                        print(f'{datetime.now()} Getting nakamas')
                        strn = ''
                        with open("bindings.json", 'r') as file:
                            data = json.load(file)
                            for key, val in data.items():
                                user = get_user_data(key)
                                strn += f"{user[0]['first_name']} {user[0]['last_name']} - {mal.url_mal + val}\n"
                            send_msg(event,
                                     "Ссылки на ребят:\n%s" % strn)

                    if event.obj.text.lower() == "/mustw":
                        send_msg(event, "Ссылка на MUSTWATCH список:",
                                 'https://docs.google.com/document/d/1aOsjs9C8mqcOasVvgqwKkzGDTfGHvAKgNWN0x--H6lk/edit')

                    if event.obj.text[:5].lower() == "/roll":
                        print(f"{str(datetime.now())} Rolling random title...")
                        data = {}
                        with open("bindings.json", 'r') as file:
                            data = json.load(file)
                        res = mal.roll_ptw(data[str(event.obj.from_id)])
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

                    if event.obj.text[:7].lower() == '/setrss':
                        print(f"{str(datetime.now())} Setting RSS...")
                        args=event.obj.text.split(' ')[1:]
                        if not event.chat_id == 3:
                            with open("bindings.json", 'r') as file:
                                data = json.load(file)
                            res = mal.get_ongoing(data[str(event.obj.from_id)])
                            with open('subrss.json', 'r+') as file:
                                lst = json.load(file)
                                lst[str(event.obj.from_id)] = (res, args)
                                file.seek(0)
                                json.dump(lst, file)
                                file.truncate()
                            msg = "Список Ваших онгоингов получен успешно!\nДля управления рассылкой доступны следующие команды:\n/updrss <add/del> [titles] - обновить список тайтлов, add - дбавить, del удалить \n/getrss -"
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
                        if not event.obj['attachments'] is None:
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

                    if event.obj.text == "/help":
                        print(f"{str(datetime.now())} print help")
                        message = 'Добро пожловать в наш уютный чатик!\nСписок команд:\nGlobal:\n/help - помощь.\n/bind <MAL-username> - привязка MAL-аккаунта к беседе по имени профиля.\n/nakama - Получить список МАЛа собеседников.\n/sauce - при отправке вложения пытается определить тайтл на скриншоте. Это должен быть оригинальный необрезанный скриншот с контентом.\n/mustw - (пока что) ссылка на MUSTWATCH список\n/roll - Рандомный тайтл из Вашего ПТВ\n/rss <new, sub, unsub> [arg] - редактировать список каналов\n-new <link> - добавить новый канал по ссылке\n-sub <name> - подписаться на канал\n-unsub <name> - отписаться от канала\nDirect:\n/setrss  - Получить список оноингов для рассылок (только в ЛС)\n/updrss <add/del> [titles] - обновить список тайтлов, add - дбавить, del удалить\n/seerss - посмотреть список тайтлов для рассылки\n'
                        send_msg(event, message)
                    
                    if event.obj.from_id == 131863240 and event.obj.text == "/kill":
                        private_msg(131863240,"Terminating WeeaBot...")
                        exit(1)

        except KeyboardInterrupt as e:
            send_msg(3,"今はここから消えたくありません…(╥﹏╥)","photo-117602761_457239215")
            exit(1)
        except requests.exceptions.ReadTimeout as timeout:
            print(f'{datetime.now()} timeout!')
            continue    
        except (requests.exceptions.ConnectionError,socket.gaierror,urllib3.exceptions.NewConnectionError,urllib3.exceptions.ProtocolError,TimeoutError) as cerror:
            start_time=time.time()
            print(f'{datetime.now()} {cerror}')
#           if time.time() > start_time + 30.0:
#              raise Exception('Unable to establish connection')
#           else:
            time.sleep(3)

def notify(uid=None):
    if uid is None:
        with open('subrss.json','r') as sfile:
            subs = json.load(sfile)
            for key,val in subs.items():
                for feed in val[1]:
                    msg=f'{feed} >'
                    with open(f'{feed}.json','r') as file:
                        titles = json.load(file)
                        res = {k: v for d in titles for k, v in d.items()}
                        for item in val[0]:
                            for tkey,tval in res.items(): 
                                if item in tkey:
                                    msg+=f'\n{tkey} - {tval}'
                    if not msg.split('>')[1] =='':
                        private_msg(int(key),msg)

if __name__ == '__main__':
    main()
