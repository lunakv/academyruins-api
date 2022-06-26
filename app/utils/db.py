import datetime
import os
from typing import Union

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
        return res['rule']


async def fetch_all_rules():
    query = 'SELECT data FROM cr ORDER BY creation_day DESC LIMIT 1'
    res = await _fetch_one(query, None)
    return res['data']


async def get_redirect(resource: str):
    query = 'SELECT link FROM redirects WHERE resource = %s'
    res = await _fetch_one(query, (resource,))
    if res:
        return res['link']


async def get_pending(resource: str):
    query = 'SELECT link FROM redirects_pending WHERE resource = %s'
    res = await _fetch_one(query, (resource,))
    if res:
        return res['link']


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
    query = 'SELECT diffs.creation_day, changes, source.set_name AS source_set, dest.set_name AS dest_set ' \
            'FROM cr_diffs AS diffs ' \
            'JOIN cr AS source ON source_id = source.id ' \
            'JOIN cr AS dest ON dest_id = dest.id ' \
            'WHERE source.set_code = %s AND dest.set_code = %s'
    result = await _fetch_one(query, (old_set_code, new_set_code))
    return result


async def fetch_pending_diff():
    query = 'SELECT changes, set_name AS source_set ' \
            'FROM cr_diffs_pending JOIN cr ON source_id = cr.id'
    res = await _fetch_one(query, None)
    return res


async def fetch_latest_diff_code():
    query = 'SELECT source.set_code AS old, dest.set_code AS new ' \
            'FROM cr_diffs AS diffs ' \
            'JOIN cr AS source ON source_id = source.id ' \
            'JOIN cr AS dest ON dest_id = dest.id ' \
            'ORDER BY diffs.creation_day DESC ' \
            'LIMIT 1'
    result = await _fetch_one(query, ())
    return result


async def fetch_diff_codes(old_code: Union[str, None], new_code: Union[str, None]):
    if old_code is None and new_code is None:
        return None
    query = 'SELECT source.set_code AS old, dest.set_code AS new ' \
            'FROM cr_diffs ' \
            'JOIN cr AS source ON source_id = source.id ' \
            'JOIN cr AS dest ON dest_id = dest.id'
    if old_code is None:
        query += ' WHERE dest.set_code = %s'
        params = (new_code,)
    else:
        query += ' WHERE source.set_code = %s'
        params = (old_code,)
    result = await _fetch_one(query, params)
    return result


async def fetch_file_name(set_code: Union[str, None] = None):
    if set_code:
        query = 'SELECT file_name FROM cr WHERE set_code = %s'
        params = (set_code,)
    else:
        query = 'SELECT file_name FROM cr ORDER BY creation_day DESC LIMIT 1'
        params = None
    res = await _fetch_one(query, params)
    if res:
        return res['file_name']


async def fetch_cr_metadata():
    query = 'SELECT creation_day, set_code, set_name, file_name FROM cr ORDER BY creation_day DESC'
    return await _fetch_all(query, None)


async def fetch_cr_diff_metadata():
    query = 'SELECT src.set_code AS source_code, dst.set_code AS dest_code, ' \
            'dst.set_name AS dest_name, bulletin_url, diffs.creation_day ' \
            'FROM cr_diffs AS diffs ' \
            'JOIN cr AS src ON source_id = src.id ' \
            'JOIN cr AS dst ON dest_id = dst.id ' \
            'ORDER BY diffs.creation_day DESC'
    return await _fetch_all(query, None)


async def fetch_mtr_metadata():
    query = 'SELECT creation_day, file_name FROM mtr ORDER BY creation_day DESC'
    return await _fetch_all(query, None)


async def fetch_ipg_metadata():
    query = 'SELECT creation_day, file_name FROM ipg ORDER BY creation_day DESC'
    return await _fetch_all(query, None)


async def upload_cr_and_diff(rules_json: dict, diff_json: list, rules_file: str):
    newCrQuery = 'INSERT INTO cr_pending (creation_day, data, file_name) ' \
                 'VALUES (%s, %s, %s) ' \
                 'RETURNING id'
    pendingCr = await _fetch_one(newCrQuery, (datetime.date.today(), Jsonb(rules_json), rules_file))

    currentCrQuery = 'SELECT id FROM cr ORDER BY creation_day DESC LIMIT 1'
    currentCr = await _fetch_one(currentCrQuery, None)

    newDiffQuery = 'INSERT INTO cr_diffs_pending (creation_day, source_id, dest_id, changes) ' \
                   'VALUES (%s, %s, %s, %s)'
    params = (datetime.date.today(), currentCr['id'], pendingCr['id'], Jsonb(diff_json))
    await _execute(newDiffQuery, params)


async def confirm_pending_cr_and_diff(set_code: str, set_name: str):
    crQuery = 'INSERT INTO cr (creation_day, set_code, set_name, data, file_name) ' \
              '(SELECT creation_day, %s, %s, data, file_name ' \
              'FROM cr_pending)' \
              'RETURNING id'
    newCr = await _fetch_one(crQuery, (set_code, set_name))

    diffQuery = 'INSERT INTO cr_diffs (creation_day, source_id, dest_id, changes) ' \
                'SELECT creation_day, source_id, %s, changes ' \
                'FROM cr_diffs_pending'
    await _execute(diffQuery, (newCr['id'],))

    deleteQuery = 'DELETE FROM cr_pending'  # cr_diffs_pending is cascaded
    await _execute(deleteQuery, None)
