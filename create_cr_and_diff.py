import asyncio
import json
import os
import sys

from app.parsing import extract_cr
from app.parsing.difftool.diffmaker import CRDiffMaker
from app.parsing.formatter import CRFormatterFactory


async def diff(old_txt, new_txt, old_set_code=None, new_set_code=None, forced_matches=None):
    old_txt = CRFormatterFactory.create_formatter(old_set_code).format(old_txt)
    new_txt = CRFormatterFactory.create_formatter(new_set_code).format(new_txt)

    old_json = await extract_cr.extract(old_txt)

    new_json = await extract_cr.extract(new_txt)
    diff_json = CRDiffMaker(forced_matches).diff(old_json["rules"], new_json["rules"])

    return old_json["rules"], new_json["rules"], diff_json


async def diff_save(old, new, forced_matches=None):
    if forced_matches:
        for i in range(len(forced_matches)):
            if type(forced_matches[i]) == str:
                forced_matches[i] = (forced_matches[i], forced_matches[i])

    # assumes the last three letters before extension are the set code
    o_code = old[-7:-4]
    n_code = new[-7:-4]
    diff_code = o_code + "-" + n_code

    with open(old, "r") as old_file:
        old_txt = old_file.read()
    with open(new, "r") as new_file:
        new_txt = new_file.read()

    old, new, dff = await diff(old_txt, new_txt, o_code, n_code, forced_matches)

    with open(os.path.join(cr_out_dir, o_code + ".json"), "w") as file:
        json.dump(old, file)
    with open(os.path.join(cr_out_dir, n_code + ".json"), "w") as file:
        json.dump(new, file)
    with open(os.path.join(diff_dir, diff_code + ".json"), "w") as file:
        json.dump(dff.diff, file)
    with open(os.path.join(maps_dir, diff_code + ".json"), "w") as file:
        json.dump(dff.matches, file)
    print(o_code, n_code)


async def diffall():
    filepaths = sorted([os.path.join(cr_in_dir, path) for path in os.listdir(cr_in_dir)], reverse=True)
    for i in range(len(filepaths) - 1):
        new = filepaths[i]
        old = filepaths[i + 1]
        await diff_save(old, new)


cr_in_dir = "app/static/raw_docs/cr"
cr_out_dir = "./gen/cr"
diff_dir = "./gen/diff"
maps_dir = "./gen/map"

if __name__ == "__main__":
    # asyncio.run(diffall())
    old = sys.argv[1]
    new = sys.argv[2]
    forced = []
    asyncio.run(diff_save(old, new, forced))
