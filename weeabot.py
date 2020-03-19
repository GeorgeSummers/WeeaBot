# coding=utf8
import mal
from vk_config import vk_token, group_id
import rss
import requests
import json
from datetime import datetime
from threading import Timer, Thread
import random
from vk_api import VkApi, VkUpload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

vk_session = VkApi(token=vk_token)

vk = vk_session.get_api()


def send_msg(chat_id, msg, att=''):
    random_id = round(random.random() * 10 ** 9)
    vk.messages.send(
        random_id=random_id,
        chat_id=chat_id,
        message=msg,
        attachment=att
    )


def get_user_data(uid):
    return vk.users.get(user_ids=int(uid))


def main():
    send_msg(3, "皆のために僕は頑張ります!\n", 'photo-117602761_457239211')
    HinoCount = 10
    while True:
        longpoll = VkBotLongPoll(vk_session, group_id, wait=15)
        upload = VkUpload(vk_session)
        print('Running WeeaBot...\n')
        try:
            for event in longpoll.listen():
                print(event.type)
                print('\n')
                if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat:

                    if event.obj.from_id == 38705372 and HinoCount == 10:
                        send_msg(
                            int(event.chat_id), "МАЛ сам себя не пофиксит.", "photo-117602761_457239139")
                        HinoCount -= 1
                        if HinoCount == 0:
                            HinoCount = 10

                    if event.obj.text[:5].lower() == '/bind':
                        print('Binding MAL')
                        usr = event.obj.text[6:]
                        try:
                            with open("bindings.json", 'r+') as file:
                                data = json.load(file)
                                data[str(event.obj.from_id)] = usr
                                print(data)
                                file.seek(0)
                                json.dump(data, file)
                                send_msg(int(event.chat_id),
                                         "Ваш MAL привязан\n" + mal.url_mal + usr)
                                continue
                        except:
                            with open("bindings.json", 'w') as f:
                                json.dump({str(event.obj.from_id): usr}, f)

                    if event.obj.text.lower() == "/nakama":
                        print('Getting nakamas')
                        strn = ''
                        with open("bindings.json", 'r') as file:
                            data = json.load(file)
                            for key, val in data.items():
                                user = get_user_data(key)
                                strn += f"{user[0]['first_name']} {user[0]['last_name']} - {mal.url_mal + val}\n"
                            send_msg(int(event.chat_id),
                                     "Ссылки на ребят:\n%s" % strn)

                    if event.obj.text.lower() == "/mustw":
                        send_msg(int(event.chat_id), "Ссылка на MUSTWATCH список:",
                                 'https://docs.google.com/document/d/1aOsjs9C8mqcOasVvgqwKkzGDTfGHvAKgNWN0x--H6lk/edit')

                    if event.obj.text[:5].lower() == "/roll":
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
                            send_msg(int(event.chat_id), f'{title}\n{stype}, {eps} Episodes\n{url}', 'photo{}_{}'.format(
                                att['owner_id'], att['id']))

                    if event.obj.text[:7].lower() == '/setrss':
                        if not event.chat_id == 3:
                            with open("bindings.json", 'r') as file:
                                data = json.load(file)
                            res = mal.get_ongoing(data[str(event.obj.from_id)])
                            with open('subrss.json', 'r+') as file:
                                lst = json.load(file)
                                lst[str(event.obj.from_id)] = (event.chat_id, res)
                                file.seek(0)
                                json.dump(lst, file)
                                file.truncate()
                            msg = "Список Ваших онгоингов получен успешно!\nДля управления рассылкой доступны следующие команды:\n/updrss -\n/getrss -"
                            send_msg(int(event.chat_id), msg)
                        else:
                            send_msg(
                                int(event.chat_id), "Для подписки на рассылку отправьте команду в ЛС!")

                    if event.obj.text == "/help":
                        message = 'Добро пожловать в наш уютный чатик!\nСписок команд:\n  Global:\n/help - помощь.\n/bind <MAL-username> - привязка MAL-аккаунта к беседе по имени профиля.\n/nakama - Получить список МАЛа собеседников.\n/mustw - (пока что) ссылка на MUSTWATCH список\n/roll - Рандомный тайтл из Вашего ПТВ\nDirect:\n/setrss  - Получить список оноингов для рассылок (только в ЛС)\n'
                        send_msg(int(event.chat_id), message)
        except requests.exceptions.ReadTimeout as timeout:
            print('timeout!')
            continue    


main()
