import re

from src.cr import service as cr_service

keyword_regex = r"702.(?:[2-9]|\d\d+)"
keyword_action_regex = r"701.(?:[2-9]|\d\d+)"
ability_words_rule = "207.2c"

# is just rule definition (ends with a number) - we want subrules
definition = r".*\d$"
# is just a single sentence (only one period) and includes "is a(n)"
single_sentence = r"^([^.]*\bis an?\b[^.]*\.)$"
# should be skipped because reasons
exceptions = ["702.57a", "702.22b"]


def should_skip(rule):
    return (
        re.match(single_sentence, rule["ruleText"])
        or re.match(definition, rule["ruleNumber"])
        or rule["ruleNumber"] in exceptions
    )


def get_keyword_definition(db, rule_id):
    """Keyword rules are not very useful in isolation. For example, 702.3 just says 'Defender'. To get the actual
    definition, we need to go to the sub-rules. Most of the time, the first sub-rule has the definition,
    but sometimes it doesn't (for example 702.3a just says 'Defender is a static ability.' which isn't particularly
    useful). This method uses a simple regex heuristic to find the sub-rule that's most likely to be a keyword's
    definition."""
    rule = cr_service.get_rule(db, rule_id)
    while should_skip(rule):
        next_rule = rule["navigation"]["nextRule"]
        if not next_rule:
            break  # stop at the end of the road
        next_rule = cr_service.get_rule(db, next_rule)
        if not next_rule or re.match(definition, next_rule["ruleNumber"]):
            break  # stop at the end of the rule
        rule = next_rule
    return rule


def get_best_rule(db, rule_id):
    if re.fullmatch(keyword_action_regex, rule_id):
        return cr_service.get_rule(db, rule_id + "a")
    elif re.fullmatch(keyword_regex, rule_id):
        return get_keyword_definition(db, rule_id)
    else:
        return cr_service.get_rule(db, rule_id)  # TODO optimize connections
