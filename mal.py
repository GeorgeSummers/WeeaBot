from jikanpy import Jikan
import random

url_mal ='https://myanimelist.net/profile/'
url_mala ='https://myanimelist.net/animelist/'
url_malm ='https://myanimelist.net/mangalist/'

jikan = Jikan()

def get_user(user,req,arg,param=None):
    return jikan.user(username=user,request=req,argument=arg,parameters=param)

def roll_ptw(usr):
    lst = get_user(usr,"animelist","plantowatch")['anime']
    newList = []
    for i in lst:
        if i['airing_status']==2:
            newList.append(i)
            continue
    return random.choice(newList)

def get_ongoing(usr):
    lst = get_user(usr,"animelist","watching")['anime']
    newList = []
    for i in lst:
        if i['airing_status']==1:
            newList.append(i)
            continue
    return newList