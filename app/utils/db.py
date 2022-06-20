import datetime
import os
from typing import Union

import anyio

import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

_constr = f'postgres://{os.environ["DB_USER"]}:{os.environ["DB_PASS"]}@{os.environ["DB_HOST"]}/{os.environ["DB_DATABASE"]}'


async def _query(query, params, exec_callback):
    if isinstance(query, list):
        queryList = query
    else:
        queryList = [query]

    async with await psycopg.AsyncConnection.connect(_constr, row_factory=dict_row) as aconn:
        async with aconn.cursor() as acur:
            for elem in queryList:
                await acur.execute(elem, params)
            if exec_callback:
                return await exec_callback(acur)


async def _execute(query, params):
    await _query(query, params, None)


async def _fetch_one(query, params):
    return await _query(query, params, lambda cur: cur.fetchone())


async def _fetch_all(query, params):
    return await _query(query, params, lambda cur: cur.fetchall())


async def fetch_rule(number):
    query = sql.SQL("SELECT data -> {} AS rule FROM cr ORDER BY creation_day DESC LIMIT 1").format(sql.Literal(number))

    res = await _fetch_one(query, None)
    if res:
        return res.rule


async def save_rules(rule_dict):
    query = "INSERT INTO cr (creation_day, set_code, set_name, data) VALUES (%s, %s, %s, %s)"
    params = (datetime.date.today(), 'TST', 'TEST', Jsonb(rule_dict))  # TODO insert actual metadata
    await _execute(query, params)


async def fetch_all_rules():
    query = 'SELECT data FROM cr ORDER BY creation_day DESC LIMIT 1'  # TODO filter out pending rules?
    res = await _fetch_one(query, None)
    return res.data


async def get_redirect(resource: str):
    query = 'SELECT link FROM redirects WHERE resource = %s'
    res = await _fetch_one(query, (resource,))
    if res:
        return res.link


async def get_pending(resource: str):
    query = 'SELECT link FROM redirects_pending WHERE resource = %s'
    res = await _fetch_one(query, (resource,))
    if res:
        return res.link


async def update_from_pending(resource: str):
    upsertQuery = 'INSERT INTO redirects (resource, link) ' \
            'SELECT resource, link ' \
            'FROM redirects_pending ' \
            'WHERE resource = %s ' \
            'ON CONFLICT (resource) ' \
            'DO UPDATE SET link = EXCLUDED.link'

    deleteQuery = 'DELETE FROM redirects_pending WHERE resource = %s'
    await _execute([upsertQuery, deleteQuery], (resource,))


async def set_pending(resource: str, link: str):
    query = 'INSERT INTO redirects_pending (resource, link) ' \
            'VALUES (%s, %s) ' \
            'ON CONFLICT (resource) ' \
            'DO UPDATE SET link = EXCLUDED.link'
    await _execute(query, (resource, link))


async def fetch_diff(old_set_code: str, new_set_code: str):
    query = 'SELECT * FROM cr_diffs ' \
            'WHERE source_code = %s AND dest_code = %s'
    result = await _fetch_one(query, (old_set_code, new_set_code))
    return result


async def fetch_latest_diff_code():
    query = 'SELECT source_code AS old, dest_code AS new FROM cr_diffs ' \
            'ORDER BY creation_day DESC ' \
            'LIMIT 1'
    result = await _fetch_one(query, ())
    return result


async def fetch_diff_codes(old_code: Union[str, None], new_code: Union[str, None]):
    if old_code is None and new_code is None:
        return None
    query = 'SELECT source_code AS old, dest_code AS new FROM cr_diffs'
    if old_code is None:
        query += ' WHERE dest_code = %s'
        params = (new_code,)
    else:
        query += ' WHERE source_code = %s'
        params = (old_code,)
    result = await _fetch_one(query, params)
    return result


async def fetch_file_name(set_code: str):
    query = 'SELECT file_name FROM cr WHERE set_code = %s'
    res = await _fetch_one(query, (set_code,))
    if res:
        return res['file_name']


async def fetch_cr_metadata():
    query = 'SELECT creation_day, set_code, set_name, file_name FROM cr ORDER BY creation_day DESC'
    return await _fetch_all(query, None)


async def upload_diff(diff_json: list):
    query = 'INSERT INTO cr_diffs (creation_day, source_set, source_code, dest_set, dest_code, changes) ' \
            'VALUES (%s, %s, %s, %s, %s, %s)'  # TODO actual metadata
    values = (datetime.date.today(), 'Streets of New Capenna', 'SNC', 'Baldur\'s Gate', 'CLB', Jsonb(diff_json))
    await _execute(query, values)
