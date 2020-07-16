from jikanpy import Jikan
import logging
import requests
import random

logger = logging.getLogger(__name__)
logger.warning('logging from mal on import')

url_mal ='https://myanimelist.net/profile/'
url_mala ='https://myanimelist.net/animelist/'
url_malm ='https://myanimelist.net/mangalist/'

jikan = Jikan()

def get_user(user,req,arg,param=None):
    return jikan.user(username=user,request=req,argument=arg,parameters=param)

def roll(usr,attr="plantowatch"):
    newList = []
    if attr=='ptw':
        attr = "plantowatch"
    for i in get_user(usr,"animelist",attr)['anime']:
        if i['airing_status']==2:
            newList.append(i)
            continue
    if not newList ==[]:
        return random.choice(newList)
    else: 
        return []

def get_ongoing(usr):
    newList = []
    for i in get_user(usr,"animelist","watching")['anime']:
        if i['airing_status']==1:
            newList.append(i['title'].replace(' (TV)',''))
            continue
    return newList

def search(title,param=None):
    logger.warning(title)
    try:
        result = jikan.search('anime',title,parameters=param)['results'][0]
        title = result['title']
        url = result['url']
        image = result['image_url']
        with requests.Session() as session:
            img = session.get(image, stream=True)
        return title,url,img.raw
    except Exception as ex:
        logger.error(ex)
        


