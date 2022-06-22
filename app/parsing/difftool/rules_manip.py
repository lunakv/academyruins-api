import difflib
import re

from . import sort_utils


def ensure_real_match(rule, some_list):
    keyword_list = ['attacking', 'attackers.',
                    'blocking', 'blockers.']
    problem_children = ['716.1a', '716.1b', '716.1c', '716.1d', '716.1e',
                        '716.1f', '716.2a', '716.2b', '716.2c', '716.2d',
                        '716.2e', '716.2f']
    for index, comparison in enumerate(some_list):
        if len(rule) == len(comparison):
            difference = list(set(rule[1:])
                              .symmetric_difference(set(comparison[1:])))
            if (len(difference) > 0 and
                    all(word in keyword_list for word in difference)):
                return some_list[1]
            if (rule[0] in problem_children):
                if (rule[0][3:] == comparison[0][3:]):
                    return some_list[index]
    return some_list[0]


def extract_rules(entire_doc):
    """Get rules out of an input Comprehensive Rules doc.

    At the moment this does intentionally leave some things off,
    most notably rule '808.' This is not a feature, it's a hack.

    Keyword arguments:
    input_file -- the CR file you want to strip rules from
    """
    # Handle editorial snafus on WotC's end
    # TODO centralize these replacements
    entire_doc = entire_doc.replace(" \"", " “")
    entire_doc = entire_doc.replace("(\"", "(“")
    entire_doc = entire_doc.replace("\"", "”")
    entire_doc = entire_doc.replace("'", "’")
    entire_doc = entire_doc.replace(" ’", " ‘")
    entire_doc = entire_doc.replace("-", "—")
    entire_doc = re.sub(r"(\w)—(\w)", r"\1–\2", entire_doc)
    entire_doc = entire_doc.replace("(tm)", "™")
    entire_doc = entire_doc.replace("(r)", "®")
    entire_doc = re.sub(r"\n\s{4,}(\w)", r" \1", entire_doc)

    extracted_rules = re.findall(r'^\d{3}[^a-zA-Z\n]{2}.*[“"”.) :]$',
                                 entire_doc, re.MULTILINE)
    rules_list = []
    for rule in extracted_rules:
        rule_normalized = rule.split()
        rule_normalized[0] = rule_normalized[0].rstrip('.')
        rules_list.append(rule_normalized)

    return rules_list


def aggregate_rule_nums(first_rules, second_rules):
    """Aggregate rule numbers.

    Aggregates the rules numbers (NOT the rules themselves)
    so we can ensure two things:
    1. Each list has the same number of elements, so it's
       easier to fiddle with later
    2. It allows placeholders for e.g. if there's a new rule
       with no relevant partner in the old rules

    Keyword arguments:
    first_rules -- the older list of rules
    second_rules -- the newer list of rules
    """
    first_rule_numbers = [i[0] for i in first_rules]
    second_rule_numbers = [i[0] for i in second_rules]

    unique_rules = set(first_rule_numbers) ^ set(second_rule_numbers)

    for index in unique_rules:
        placeholder = [index, '']

        if index not in first_rule_numbers:
            first_rules.append(placeholder)

        if index not in second_rule_numbers:
            second_rules.append(placeholder)

    sort_utils.insertion_sort(first_rules)
    sort_utils.insertion_sort(second_rules)

    complete_rules_list = [word for word in first_rules]
    return complete_rules_list


def align_matches(some_list, match_list):
    """Find most likely match from old rule -> new rule

    Compares rules in the first list to its close neighbors
    to determine if there's a better rule it should actually be
    compared to.
    For instance, if the new rules insert a new 202.3d, which pushes
    old!202.3d 'down' a space, old!202.3d should actually be diffed
    against new!202.3e

    Keyword arguments:
    some_list -- the older list of rules
    match_list -- the newer list of rules
    """
    homeless_rules = []
    for index, rule in enumerate(some_list):
        best = difflib.get_close_matches(
            rule,
            match_list,
            cutoff=.4)
        try:
            if len(best) == 0:
                raise IndexError
            match = ensure_real_match(rule, best)
            swap_index = match_list.index(match)
        except IndexError:
            continue
        else:
            if swap_index != index:
                # Can't swap in place because it might alienate
                # rules later in the list
                homeless_rules.append((swap_index, rule))
                placeholder = [rule[0], '']
                some_list[some_list.index(rule)] = placeholder

    for index, rule in homeless_rules:
        some_list[index] = list(rule)
