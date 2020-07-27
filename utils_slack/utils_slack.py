import requests
import json

import constants
import logging
logging.getLogger().setLevel(logging.INFO)


def send_message(channel_name, message='no-data'):
    wekbook_url = constants.slack.get(channel_name, None)
    data = {'text': message}
    response = requests.post(wekbook_url, data=json.dumps(
        data), headers={'Content-Type': 'application/json'})
    logging.info('Response: ' + str(response.text))
    logging.info('Response code: ' + str(response.status_code))
    return response
