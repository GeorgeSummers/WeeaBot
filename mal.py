from jikanpy import Jikan
import requests
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

def search(title):
    result = jikan.search('anime',title)['results'][0]
    title = result['title']
    url = result['url']
    image = result['image_url']
    with requests.Session() as session:
        img = session.get(image, stream=True)
    return title,url,img.raw
