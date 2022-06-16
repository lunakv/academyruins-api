import datetime
import os
import anyio

import psycopg
from psycopg import sql
from psycopg.types.json import Jsonb

_constr = f'postgres://{os.environ["DB_USER"]}:{os.environ["DB_PASS"]}@{os.environ["DB_HOST"]}/{os.environ["DB_DATABASE"]}'


async def _query(query, params, exec_callback):
    if isinstance(query, list):
        queryList = query
    else:
        queryList = [query]

    async with await psycopg.AsyncConnection.connect(_constr) as aconn:
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
    query = sql.SQL("SELECT data -> {} FROM cr ORDER BY creation_day DESC LIMIT 1").format(sql.Literal(number))

    res = await _fetch_one(query, None)
    if res:
        return res[0]


async def save_rules(rule_dict):
    query = "INSERT INTO cr (creation_day, set_code, set_name, data) VALUES (%s, %s, %s, %s)"
    params = (datetime.date.today(), 'TST', 'TEST', Jsonb(rule_dict))
    await _execute(query, params)


async def fetch_all_rules():
    query = 'SELECT data FROM cr ORDER BY creation_day DESC LIMIT 1'
    res = (await _fetch_one(query, None))[0]
    return res


async def get_redirect(resource: str):
    query = 'SELECT link FROM redirects WHERE resource = %s'
    res = await _fetch_one(query, (resource,))
    if res:
        return res[0]


async def get_pending(resource: str):
    query = 'SELECT link FROM redirects_pending WHERE resource = %s'
    res = await _fetch_one(query, (resource,))
    if res:
        return res[0]


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
