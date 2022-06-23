import json
import requests
import re
import datetime

from ..resources.cache import KeywordCache, GlossaryCache
from ..resources import static_paths as paths
from ..utils import db
from . import extract_cr
from .difftool import diff_rules
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
    file_name = 'cr-' + datetime.date.today().isoformat() + '.txt'
    file_path = paths.cr_dir + '/' + file_name
    with open(file_path, 'w', encoding='utf-8') as output:
        output.write(text)
    with open(paths.current_cr, 'w', encoding='utf-8') as output:
        output.write(text)

    return text, file_name


async def refresh_cr(link):
    if link is None:
        link = await db.get_redirect('cr')
    new_text, file_name = download_cr(link)
    result = await extract_cr.extract(new_text)
    current_cr_path = paths.current_cr
    with open(current_cr_path, 'r') as curr_file:
        current_text = curr_file.read()

    diff_json = diff_rules.diff_cr(current_text, new_text)
    # TODO add to database instead
    KeywordCache().replace(result['keywords'])
    GlossaryCache().replace(result['glossary'])
    await db.upload_cr_and_diff(result['rules'], diff_json, file_name)


if __name__ == '__main__':
    refresh_cr(None)
