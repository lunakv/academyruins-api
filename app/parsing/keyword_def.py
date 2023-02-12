import re

from ..database import operations as ops
from .extract_cr import keyword_action_regex, keyword_regex

# is just rule definition (ends with a number) - we want subrules
definition = r".*\d$"
# is just a single sentence (only one comma) and includes "is a(n)"
single_sentence = r"^([^.]*\bis an?\b[^.]*\.)$"
# should be skipped because reasons
exceptions = ["702.57a", "702.22b"]


def should_skip(rule):
    return (
        re.match(single_sentence, rule["ruleText"])
        or re.match(definition, rule["ruleNumber"])
        or rule["ruleNumber"] in exceptions
    )


async def get_keyword_definition(db, rule_id):
    """Keyword rules are not very useful in isolation. For example, 702.3 just says 'Defender'. To get the actual
    definition, we need to go to the sub-rules. Most of the time, the first sub-rule has the definition,
    but sometimes it doesn't (for example 702.3a just says 'Defender is a static ability.' which isn't particularly
    useful). This method uses a simple regex heuristic to find the sub-rule that's most likely to be a keyword's
    definition."""
    rule = ops.get_rule(db, rule_id)
    while should_skip(rule):
        next_rule = rule["navigation"]["nextRule"]
        if not next_rule:
            break  # stop at the end of the road
        next_rule = ops.get_rule(db, next_rule)
        if re.match(definition, next_rule["ruleNumber"]):
            break  # stop at the end of the rule
        rule = next_rule
    return rule


async def get_best_rule(db, rule_id):
    if re.fullmatch(keyword_action_regex, rule_id):
        return ops.get_rule(db, rule_id + "a")
    elif re.fullmatch(keyword_regex, rule_id):
        return await get_keyword_definition(db, rule_id)
    else:
        return ops.get_rule(db, rule_id)  # TODO optimize connections
