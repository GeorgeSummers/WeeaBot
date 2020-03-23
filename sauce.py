import requests
import json

def get_sauce(image):
    response =  requests.post("https://trace.moe/api/search",data={"image":image}).content
    return json.loads(response)['docs'][0]

def pic_sauce():
    pass