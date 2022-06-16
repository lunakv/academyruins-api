import json
import requests
import re
import datetime
from ..resources import static_paths as paths
from ..utils import db
from . import extract_cr
import logging


def download_cr(uri):
    response = requests.get(uri)
    if not response.ok:
        logging.error(f"Couldn't download CR from link (code {response.status_code}). Tried link: {uri}")
        return

    response.encoding = 'utf-8'
    text = response.text
    # replace CR and CRLF with LF
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # remove BOM
    bom = re.compile('^\xEF\xBB\xBF')
    text = re.sub(bom, '', text)

    # save to file
    file_name = paths.cr_dir + '/cr-' + datetime.date.today().isoformat() + '.txt'
    with open(file_name, 'w', encoding='utf-8') as output:
        output.write(text)
    with open(paths.current_cr, 'w', encoding='utf-8') as output:
        output.write(text)

    return text


async def refresh_cr():
    link = await db.get_redirect('cr')
    download_cr(link)
    await extract_cr.extract(paths.current_cr)


if __name__ == '__main__':
    refresh_cr()
