import json

from . import diff_utils
from . import rules_manip


def diff_cr(orig_cr, dest_cr, forced_matches: list[tuple]):
    # old_rules = rules_manip.extract_rules(orig_cr)
    # new_rules = rules_manip.extract_rules(dest_cr)
    old_rules = orig_cr
    new_rules = dest_cr

    # rules_manip.aggregate_rule_nums(old_rules, new_rules)
    matches = rules_manip.align_matches(old_rules, new_rules, forced_matches)

    rules = []
    changes = []  # not currently utilized
    deletions = []  # not currently utilized

    for match in matches:
        if match[0] == "608.2f":
            print(1)
        comparison = diff_utils.diff_rules(match, old_rules, new_rules)
        if comparison:
            rules.append(comparison)

    rules.sort(key=lambda item: item["new"]["ruleNum"] if item["new"] else item["old"]["ruleNum"])
    return rules


if __name__ == "__main__":
    # Arg list looks like this:
    # old CR file, ~~old file set name (e.g. "Guilds of Ravnica")~~,
    # new CR file, ~~new file set name~~
    # orig_cr, dest_cr = sys.argv[1], sys.argv[2]
    cr_dir = "../../../cr/"
    orig_path = cr_dir + "SNC.json"
    dest_path = cr_dir + "CLB.json"
    # This is explicitly done because I have complete control over the file
    # naming convention I use. This is N O T the best way to do this, but
    # I didn't want to futz with regex here.
    #  orig_cr_set_code = orig_cr[-7:-4]
    #  dest_cr_set_code = dest_cr[-7:-4]
    with open(orig_path, "r") as orig_file, open(dest_path, "r") as dest_file:
        orig = json.load(orig_file)
        dest = json.load(dest_file)
    diff_cr(orig, dest)
    print()
