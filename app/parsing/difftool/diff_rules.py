from . import diff_utils
from . import rules_manip


def diff_cr(orig_cr, dest_cr):
    # TODO this could work on parsed rule JSONs instead of raw text files
    old_rules = rules_manip.extract_rules(orig_cr)
    new_rules = rules_manip.extract_rules(dest_cr)

    rules_manip.aggregate_rule_nums(old_rules, new_rules)
    rules_manip.align_matches(old_rules, new_rules)

    rules = []
    changes = []  # not currently utilized
    deletions = []  # not currently utilized

    for i, (old, new) in enumerate(zip(old_rules, new_rules)):
        output_comparison = diff_utils.diff_rules(old, new)
        if output_comparison:
            rules.append(output_comparison)
            if output_comparison["old"] and output_comparison["new"]:
                if output_comparison["old"]["ruleNum"] != output_comparison["new"]["ruleNum"]:
                    changes.append(
                        {"old": output_comparison["old"]["ruleNum"], "new": output_comparison["new"]["ruleNum"]}
                    )

            if output_comparison["old"] and not output_comparison["new"]:
                deletions.append({"removed": output_comparison["old"]["ruleNum"]})

    return rules
    # finished_changes = {'lastUpdate':
    #                     datetime.datetime.today().strftime('%Y-%d-%m'),
    #                     'changes': changes,
    #                     'deletions': deletions}
    # out_changes.write(json.dumps(finished_changes, indent=4))


if __name__ == "__main__":
    # Arg list looks like this:
    # old CR file, ~~old file set name (e.g. "Guilds of Ravnica")~~,
    # new CR file, ~~new file set name~~
    # orig_cr, dest_cr = sys.argv[1], sys.argv[2]
    cr_dir = "../../static/raw_docs/cr/"
    orig_path = cr_dir + "cr-2021-07-23-AFR.txt"
    dest_path = cr_dir + "cr-2021-09-24-MID.txt"
    # This is explicitly done because I have complete control over the file
    # naming convention I use. This is N O T the best way to do this, but
    # I didn't want to futz with regex here.
    #  orig_cr_set_code = orig_cr[-7:-4]
    #  dest_cr_set_code = dest_cr[-7:-4]
    with open(orig_path, "r") as orig_file, open(dest_path, "r") as dest_file:
        orig = orig_file.read()
        dest = dest_file.read()
    diff_cr(orig, dest)
    print()
