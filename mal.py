from jikanpy import Jikan

url_mal ='https://myanimelist.net/profile/'
url_mala ='https://myanimelist.net/animelist/'
url_malm ='https://myanimelist.net/mangalist/'

jikan = Jikan()

def get_user(user,req,arg,param=None):
    return jikan.user(username=user,request=req,argument=arg,parameters=param)
