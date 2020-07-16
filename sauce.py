import requests
import json
import logging


logger = logging.getLogger(__name__)
logger.warning('logging from sauce on import')

def get_sauce(image):
    response =  requests.post("https://trace.moe/api/search",data={"image":image}).content
    return json.loads(response)['docs'][0]

def pic_sauce():
    pass