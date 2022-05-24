import json
import requests
import re
import datetime
import static_paths
import extract_cr



def download_cr(uri):
    response = requests.get(uri)
    if not response.ok:
        # print error
        return
    
    response.encoding = 'utf-8'
    text = response.text
    # replace CR and CRLF with LF
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # remove BOM
    bom = re.compile('^\xEF\xBB\xBF')
    text = re.sub(bom, '', text)

    # save to file
    file_name = static_paths.cr_dir + '/cr-' + datetime.date.today().isoformat() + '.txt'
    with open(file_name, 'w', encoding='utf-8') as output:
        output.write(text)
    with open(static_paths.current_cr, 'w', encoding='utf-8') as output:
        output.write(text)

    return text

def refresh_cr():
    redirects = {}
    with open(static_paths.redirects, 'r') as dict:
        redirects = json.load(dict)
    
    download_cr(redirects['cr'])
    extract_cr.extract(static_paths.current_cr)

if __name__ == '__main__':
    refresh_cr()