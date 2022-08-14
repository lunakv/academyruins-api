import difflib
import re

from app.parsing.difftool.matchscoregraph import MatchScoreGraph


def ensure_real_match(rule, some_list):
    keyword_list = ["attacking", "attackers.", "blocking", "blockers."]
    problem_children = [
        "716.1a",
        "716.1b",
        "716.1c",
        "716.1d",
        "716.1e",
        "716.1f",
        "716.2a",
        "716.2b",
        "716.2c",
        "716.2d",
        "716.2e",
        "716.2f",
    ]
    for index, comparison in enumerate(some_list):
        if len(rule) == len(comparison):
            difference = list(set(rule[1:]).symmetric_difference(set(comparison[1:])))
            if len(difference) > 0 and all(word in keyword_list for word in difference):
                return some_list[1]
            if rule[0] in problem_children:
                if rule[0][3:] == comparison[0][3:]:
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
    entire_doc = entire_doc.replace(' "', " “")
    entire_doc = entire_doc.replace('("', "(“")
    entire_doc = entire_doc.replace('"', "”")
    entire_doc = entire_doc.replace("'", "’")
    entire_doc = entire_doc.replace(" ’", " ‘")
    entire_doc = entire_doc.replace("-", "—")
    entire_doc = re.sub(r"(\w)—(\w)", r"\1–\2", entire_doc)
    entire_doc = entire_doc.replace("(tm)", "™")
    entire_doc = entire_doc.replace("(r)", "®")
    entire_doc = re.sub(r"\n\s{4,}(\w)", r" \1", entire_doc)

    extracted_rules = re.findall(r'^\d{3}[^a-zA-Z\n]{2}.*[“"”.) :]$', entire_doc, re.MULTILINE)
    rules_list = []
    for rule in extracted_rules:
        rule_normalized = rule.split()
        rule_normalized[0] = rule_normalized[0].rstrip(".")
        rules_list.append(rule_normalized)

    return rules_list


def aggregate_rule_nums(first_rules: dict, second_rules: dict):
    """
    Aggregate rule numbers.

    Aggregates the rules numbers (NOT the rules themselves)
    so we can ensure two things:
    1. Each list has the same number of elements, so it's
       easier to fiddle with later
    2. It allows placeholders for e.g. if there's a new rule
       with no relevant partner in the old rules

    Keyword arguments:
    first_rules -- the older rules dict
    second_rules -- the newer rules dict
    """
    first_rule_numbers = first_rules.keys()
    second_rule_numbers = second_rules.keys()

    unique_rules = set(first_rule_numbers) ^ set(second_rule_numbers)

    for index in unique_rules:
        if index not in first_rule_numbers:
            first_rules[index] = ""

        if index not in second_rule_numbers:
            second_rules[index] = ""


def prune_unchanged_rules(old_rules: dict, new_rules: dict) -> None:
    to_purge = []
    for num in old_rules:
        if num in new_rules and old_rules[num]["ruleText"] == new_rules[num]["ruleText"]:
            to_purge.append(num)

    for num in to_purge:
        del new_rules[num]
        del old_rules[num]


def align_matches(old_unmatched: dict, new_unmatched: dict, forced_matches: list[tuple]):
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

    old_unmatched = old_unmatched.copy()
    new_unmatched = new_unmatched.copy()

    matched_rules = []
    for o, n in forced_matches:
        matched_rules.append((o, n))
        del old_unmatched[o]
        del new_unmatched[n]
    prune_unchanged_rules(old_unmatched, new_unmatched)

    new_texts = [val["ruleText"] for val in new_unmatched.values()]

    score_graph = MatchScoreGraph()

    for num in old_unmatched:
        old_text = old_unmatched[num]["ruleText"].split(" ")

        best_matches = difflib.get_close_matches(old_text, [x.split(" ") for x in new_texts], cutoff=0.4)
        if "705" in num:
            print()
        for match in best_matches:
            new_num = next(filter(lambda value: value["ruleText"] == " ".join(match), new_unmatched.values()))[
                "ruleNumber"
            ]
            score = difflib.SequenceMatcher(None, match, old_text).ratio()
            score_graph.add_edge(new_num, num, score)

    while score_graph.edge_count > 0:
        new_num, old_num, weight = score_graph.get_max_edge()
        matched_rules.append((old_num, new_num))
        del old_unmatched[old_num]
        del new_unmatched[new_num]
        score_graph.remove_nodes(new_num, old_num)

    for old in old_unmatched:
        matched_rules.append((old, None))
    for new in new_unmatched:
        matched_rules.append((None, new))
    return matched_rules
