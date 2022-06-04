import requests
import re
from bs4 import BeautifulSoup
from ..utils.notifier import notify_scrape_error, notify_new_cr
from ..resources.cache import RedirectCache
import logging

rules_page_uri = 'https://magic.wizards.com/en/rules/'
redirects = RedirectCache()


def is_txt_link(tag):
    return tag.name == 'a' and tag.has_attr('href') and re.search(r'.*\.txt', tag['href'])


def scrape_rules_page():
    if redirects.is_pending('cr'):
        logging.debug('New CR redirect already pending, skipping scrape')
        return

    response = requests.get(rules_page_uri)
    if response.status_code != requests.codes.ok:
        notify_scrape_error(f"Couldn't fetch rules page (code {response.status_code})")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    txt_links = soup.find_all(is_txt_link)
    if len(txt_links) != 1:
        notify_scrape_error(f'Wrong number of TXT links found! (expected 1, got {len(txt_links)})')
        return

    href = txt_links[0]['href']
    href = href.replace(' ', '%20')  # the last path segment sometimes has a space (kinda hacky, but whatever)

    if href != redirects.get('cr'):
        redirects.set_pending('cr', href)
        notify_new_cr(href)


if __name__ == '__main__':
    scrape_rules_page()