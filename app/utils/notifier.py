import os
import requests
from dotenv import load_dotenv

load_dotenv()
_uri = 'https://api.pushover.net/1/messages.json'
_token = os.environ.get('PUSHOVER_APP_TOKEN')
_user = os.environ.get('PUSHOVER_USER_KEY')
_refresh_uri = os.environ.get('BASE_URI', '') + '/update-cr/?token=' + os.environ.get('ADMIN_KEY')


def notify(message, title=None, uri=None, uri_title=None, formatted=None):
    if os.environ.get('USE_PUSHOVER') != '1':
        return
    payload = {'token': _token, 'user': _user, 'message': message}
    if title:
        payload['title'] = title
    if uri:
        payload['url'] = uri
    if uri_title:
        payload['url_title'] = uri_title
    if formatted:
        payload['html'] = 1

    requests.post(_uri, data=payload)


def notify_scrape_error(message):
    notify(message, title='Scraping Error')


def notify_new_cr(link):
    notify(formatted=True, message=f'New CR version is <a href="{link}">available</a> and ready to be parsed',
           title='Found new CR', uri=_refresh_uri, uri_title='Confirm Update')
