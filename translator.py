from config import wit_ctoken
from wit import Wit
import logging

logger = logging.getLogger(__name__)
client = Wit(access_token=wit_ctoken, logger=logger)

def translate(file):
    response = client.speech(file, None, {'Content-Type': 'audio/mpeg3'})
    return str(response['_text'])