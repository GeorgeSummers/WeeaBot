from jikanpy import Jikan
import random

url_mal ='https://myanimelist.net/profile/'
url_mala ='https://myanimelist.net/animelist/'
url_malm ='https://myanimelist.net/mangalist/'

jikan = Jikan()

def get_user(user,req,arg,param=None):
    return jikan.user(username=user,request=req,argument=arg,parameters=param)

def roll_ptw(usr):
    newList = []
    for i in get_user(usr,"animelist","plantowatch")['anime']:
        if i['airing_status']==2:
            newList.append(i)
            continue
    return random.choice(newList)

def get_ongoing(usr):
    newList = []
    for i in get_user(usr,"animelist","watching")['anime']:
        if i['airing_status']==1:
            newList.append(i['title'])
            continue
    return newList

def upd_ongoing(cmd,uid,titles):
    with open('subrss.json','r+') as fsub:
        data = json.load(fsub)
        for title in titles:
            if cmd == "del":
                data[str(uid)][1].remove(title)
            elif cmd == "add":
                data[str(uid)][1].append(title)
        fsub.seek(0)
        json.dump(data, fsub)
        fsub.truncate()
