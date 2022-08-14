import difflib
import re

from pathlib import Path


def get_readable_header(first_file, second_file):
    """Get the readable names from input files.

    We want our eventual final output to include headers so that people
    can easily see what versions we're diffing between. This grabs the
    files' relevant parts -- which here is /folder/{THIS PART}.extension
    for display purposes.

    Keyword arguments:
    first_file -- the file we're diffing from
    second_file -- the file we're diffing to
    """
    from_name = Path(first_file).stem
    to_name = Path(second_file).stem

    return {"old": from_name, "new": to_name}


def wrap_slice(rule_slice) -> tuple:
    """Wrap the changed rules text in tags for JSON to parse.

    This allows us to highlight changes programmatically. Javascript can
    replace the old_start, new_start, etc tags with their proper <span>
    tags in the generated HTML. Easier to handle there than here.

    Note this does NOT differentiate between inserts, replaces, deletions
    like a general diff tool.

    Keyword arguments:
    rule_slice -- the chunk of the rule that indicates a change
    status -- whether the slice belongs to an 'old' rule or a 'new' rule.
    """
    if not rule_slice:
        return "", False
    if re.match(r"^(?:rules? )?\d{3}(?:\.\d+[a-z]*)*(?:–\d{3}(?:\.\d+[a-z]?)?)?\)?\.?", " ".join(rule_slice)):
        return rule_slice, False

    rule_slice[0] = "<<<<" + rule_slice[0]
    rule_slice[-1] += ">>>>"
    return rule_slice, True


def diff_rules(match: tuple, old_rules: dict, new_rules: dict):
    """Determine how two given rules differ.

    A few things happening here:
    1. First, determine if the rule has a partner
    2. If it has a partner, make sure its partner isn't identical to it,
       so we don't waste time diffing things we can already determine to
       be the same.
    3. Once we have rules we know needs to be diffed, wrap the changes slices
       using diff_utils.wrap_slice, tidy up the strings

    Keyword arguments:
    old_rule -- the old rule to compare from
    new_rule -- the new rule to compare to
    """
    rules_comparison = {"old": {}, "new": {}}

    if not match[0]:
        return {"old": None, "new": {"ruleNum": match[1], "ruleText": new_rules[match[1]]["ruleText"]}}
    if not match[1]:
        return {"old": {"ruleNum": match[0], "ruleText": old_rules[match[0]]["ruleText"]}, "new": None}

    old_rule = old_rules[match[0]]
    new_rule = new_rules[match[1]]
    old_text = old_rule["ruleText"].strip()
    new_text = new_rule["ruleText"].strip()
    if old_text == new_text:
        return None
    # we want to diff whole words, not each char, so we split the strings into word lists
    old_text = old_text.split(" ")
    new_text = new_text.split(" ")

    # old_rule_num, new_rule_num = old_rule[0], new_rule[0]
    # old_rule_text, new_rule_text = old_rule[1:], new_rule[1:]

    seq = difflib.SequenceMatcher(None, old_text, new_text)
    matches = seq.get_matching_blocks()

    modded_old, modded_new = [], []
    old_offset, new_offset = 0, 0
    # via difflib docs: matching blocks come in a tuple such that
    # old_rule[o:o+l] == new_rule[n:n+l].
    changed = False
    for o, n, l in matches:
        slice, is_wrapped = wrap_slice(old_text[old_offset:o])
        modded_old.extend(slice)
        changed |= is_wrapped
        slice, is_wrapped = wrap_slice(new_text[new_offset:n])
        changed |= is_wrapped
        modded_new.extend(slice)

        modded_old.extend(old_text[o : o + l])
        modded_new.extend(new_text[n : n + l])
        old_offset = o + l
        new_offset = n + l

    if not changed:
        return None
    old_diff_text = " ".join(modded_old)
    new_diff_text = " ".join(modded_new)
    rules_comparison["old"] = {"ruleNum": match[0], "ruleText": old_diff_text}
    rules_comparison["new"] = {"ruleNum": match[1], "ruleText": new_diff_text}
    return rules_comparison

    for o, n, i in matches:
        if len(matches) == 1:  # A rule doesn't have a partner

            if o > n:  # Old rule was deleted
                rules_comparison["old"] = {"ruleNum": old_rule_num, "ruleText": " ".join(old_rule_text)}

                rules_comparison["new"] = None

            elif o < n:  # New rule was added
                rules_comparison["old"] = None

                rules_comparison["new"] = {"ruleNum": new_rule_num, "ruleText": " ".join(new_rule_text)}

            return rules_comparison

        # The two rules are identical, so we can discard them
        elif len(matches) == 2 and old_rule == new_rule:
            return None
        elif len(matches) == 2 and old_rule_text == new_rule_text:
            return None
        else:
            modded_old.extend(wrap_slice(old_rule_text[old_offset:o], "old"))
            modded_old.extend(old_rule_text[o : o + i])
            old_offset = o + i

            modded_new.extend(wrap_slice(new_rule_text[new_offset:n], "new"))
            modded_new.extend(new_rule_text[n : n + i])
            new_offset = n + i

    if "<<<<" not in " ".join(modded_old) and "<<<<" not in " ".join(modded_new):
        # the only changes were to rule numbers, so we can get out
        return None

    rules_comparison["old"] = {"ruleNum": old_rule_num, "ruleText": " ".join(modded_old)}
    rules_comparison["new"] = {"ruleNum": new_rule_num, "ruleText": " ".join(modded_new)}
    return rules_comparison
