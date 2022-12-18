import json
import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from app.difftool.diffmaker import MtrDiffMaker
from app.parsing.mtr.extract_mtr import extract

load_dotenv()

def mtr_to_text(effective: date, sections: list[dict]) -> str:
    ret = f'Effective {effective}\n'
    for s in sections:
        ret += f'{s["section"] or 0}.{s["subsection"] or 0} {s["title"]}\n'
        ret += (s["content"] or '') + "\n"
    return ret

def parse_and_diff(old: str, new: str):
    old_date, old_sections = extract(old)
    new_date, new_sections = extract(new)
    diff = MtrDiffMaker().diff(old_sections, new_sections).diff

    return old_date, old_sections, new_date, new_sections, diff

def diff_save(old: str, new: str):
    old_date, old_sections, new_date, new_sections, diff = parse_and_diff(old, new)
    old_file = mtr_out_dir / (old_date.isoformat() + '.json')
    new_file = mtr_out_dir / (new_date.isoformat() + '.json')
    diff_file = mtr_diff_dir / (new_date.isoformat() + '.json')
    with open(old_file, 'w') as file:
        json.dump({"effective_date": old_date.isoformat(), "content": old_sections}, file)
    with open(new_file, 'w') as file:
        json.dump({"effective_date": new_date.isoformat(), "content": new_sections}, file)
    with open(diff_file, 'w') as file:
        json.dump({"effective_date": new_date.isoformat(), "changes": diff}, file)

    old_txt = mtr_out_dir / (old_date.isoformat() + '.txt')
    new_txt = mtr_out_dir / (new_date.isoformat() + '.txt')
    with open(old_txt, 'w') as file:
        file.write(mtr_to_text(old_date, old_sections))
    with open(new_txt, 'w') as file:
        file.write(mtr_to_text(new_date, new_sections))

mtr_out_dir = Path('.') / "gen" / "mtr"
mtr_diff_dir = Path('.') / "gen" / "mtr-diff"

if __name__ == "__main__":
    old = sys.argv[1]
    new = sys.argv[2]
    diff_save(old, new)


