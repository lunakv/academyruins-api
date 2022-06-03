import os
import requests
from dotenv import load_dotenv

load_dotenv()
_uri = 'https://api.pushover.net/1/messages.json'
_token = os.environ['PUSHOVER_APP_TOKEN']
_user = os.environ['PUSHOVER_USER_KEY']
_refresh_uri = None  # TODO


def notify(message, title=None, url=None, formatted=None):
    if os.environ['USE_PUSHOVER'] != '1':
        return
    payload = {'token': _token, 'user': _user, 'message': message}
    if title: payload['title'] = title
    if url: payload['url'] = url
    if formatted: payload['html'] = 1

    requests.post(_uri, data=payload)


def notify_scrape_error(message):
    notify(message, title='Scraping Error')


def notify_new_cr(link):
    notify(formatted=True, message=f'New CR version is <a href="{link}">available</a> and ready to be parsed',
           title='Found new CR', url=_refresh_uri)
