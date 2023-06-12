import json

from dotenv import load_dotenv
from sqlalchemy import select

from app.database.models import Cr
from app.difftool.diffmaker import CRDiffMaker

load_dotenv()

import app.database.operations as ops
from app.database.db import SessionLocal

session = SessionLocal()


def get_cr(set_code):
    stmt = select(Cr.data).where(Cr.set_code == set_code)
    return session.execute(stmt).scalar_one()


def in_diff(diff, match):
    matched_list = [
        x
        for x in diff
        if diff["old"] and diff["new"] and diff["old"]["ruleNum"] == match[0] and diff["new"]["ruleNum"] == match[1]
    ]
    return len(matched_list) > 0


forced = "./gen/forced-matches"
out = "./gen/matches"

diff_list = ops.get_cr_diff_metadata(session)
cr_list = ops.get_cr_metadata(session)
for date, old_code, new_code, _, _ in diff_list:
    diff = ops.get_cr_diff(session, old_code, new_code)
    changes = diff.changes
    forced_list = []
    for change in diff.changes:
        old = change.get("old") or {}
        new = change.get("new") or {}
        forced_list.append((old.get("ruleNum"), new.get("ruleNum")))
    with open(f"{forced}/{new_code}.json", "w") as f:
        json.dump(forced_list, f)

    print("Parsing:", old_code, new_code)
    old_cr = get_cr(old_code)
    new_cr = get_cr(new_code)
    generated_diff = CRDiffMaker(forced_list).diff(old_cr, new_cr)
    with open(f"{out}/{new_code}.json", "w") as f:
        json.dump(generated_diff.moved, f)

session.close()
