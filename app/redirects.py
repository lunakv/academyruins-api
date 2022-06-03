import static_paths as paths
import json
import logging

with open(paths.redirects, 'r') as file_input:
    _dict = json.load(file_input)


def save_dict():
    with open(paths.redirects, 'w') as file_output:
        json.dump(_dict, file_output)
    logging.debug('Saved new redirects file')


def get_redirect(name):
    return _dict[name] if name in _dict else None


def has_redirect(name):
    return name in _dict


def is_pending(name):
    return 'pending' in _dict and name in _dict['pending']


def set_pending(name, value):
    if 'pending' not in _dict:
        _dict['pending'] = {}
    _dict['pending'][name] = value
    logging.info(f'Set pending redirect to {name} as {value}')
    save_dict()


def update_from_pending(name):
    if 'pending' not in _dict or name not in _dict['pending']:
        logging.error(f'Tried to update value {name}, but it has no pending value.')
        return None

    _dict[name] = _dict['pending'][name]
    del _dict['pending'][name]
    logging.info(f'Updated value {name} in redirect dictionary')
    save_dict()
    return _dict[name]
