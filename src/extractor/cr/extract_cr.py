import json
import re

from cr.keyword_def import ability_words_rule, keyword_action_regex, keyword_regex
from cr.schemas import ToCSection, ToCSubsection
from resources import static_paths as paths

# TODO rework into new class hierarchy


# parse plaintext CR into structured representations
# lifted directly from an old VensersJournal file, should be cleaned up at some point
def extract(comp_rules: str):
    rules_json = {}
    rules_flattened = {}
    glossary_json = {}

    toc = extract_toc(comp_rules)
    start_index = comp_rules.find("Glossary")
    comp_rules = comp_rules[start_index:]

    comp_rules = re.sub(r"\n\s{4,}(\w)", r" \1", comp_rules)

    sections = re.findall(r"^\d{3}\..*?(?=^\d{3}\. |Glossary)", comp_rules, re.MULTILINE | re.DOTALL)

    rule_from_previous_section = ""
    rule_object_ref = {}
    keywords = {
        "keywordAbilities": [],
        "keywordActions": [],
        "abilityWords": [],
    }

    for index, section in enumerate(sections):
        currentSection = []
        rules = re.findall(
            r"^(\d{3}\.[^\s.]{1,4})[\s.]*(.*)"
            "(?:\nExample: (.*))?(?:\nExample: (.*))?"
            "(?:\nExample: (.*))?(?:\nExample: (.*))?",
            section,
            re.MULTILINE,
        )
        for idx, rule in enumerate(rules):
            nonempty_examples = []
            for ex in rule[2:5]:
                if ex != "":
                    nonempty_examples.append(ex)
            if len(nonempty_examples) == 0:
                nonempty_examples = None

            previous_rule = ""
            next_rule = ""

            if idx - 1 < 0:
                if rule_from_previous_section:
                    previous_rule = rule_from_previous_section
                else:
                    previous_rule = None
            else:
                previous_rule = rules[idx - 1][0]

            try:
                next_rule = rules[idx + 1][0]
            except IndexError:
                next_rule = None

            try:
                if not rule_object_ref[rule_from_previous_section.split(".")[1]]["navigation"]["nextRule"]:
                    rule_object_ref[rule_from_previous_section.split(".")[1]]["navigation"]["nextRule"] = rule[0]
            except (KeyError, IndexError):
                pass
            new_rule = {
                "ruleNumber": rule[0],
                "fragment": rule[0].split(".")[1],
                "ruleText": rule[1],
                "examples": nonempty_examples,
                "navigation": {"previousRule": previous_rule, "nextRule": next_rule},
            }
            currentSection.append(new_rule)
            rules_flattened[new_rule["ruleNumber"]] = new_rule
            rule_object_ref = new_rule
            if re.fullmatch(keyword_regex, new_rule["ruleNumber"]):
                keywords["keywordAbilities"].extend(split_keywords(new_rule["ruleText"]))
            elif re.fullmatch(keyword_action_regex, new_rule["ruleNumber"]):
                keywords["keywordActions"].extend(split_keywords(new_rule["ruleText"]))
            elif new_rule["ruleNumber"] == ability_words_rule:
                keywords["abilityWords"] = split_ability_words(new_rule["ruleText"])

        previous_section = None
        next_section = None

        if index - 1 < 0:
            pass
        else:
            prev = sections[index - 1]
            previous_section = {"name": prev[: prev.find("\n")], "id": prev[:3]}
        try:
            next = sections[index + 1]
            next_section = {"name": next[: next.find("\n")], "id": next[:3]}
        except IndexError:
            pass
        rules_json[section[:3]] = {
            "rules": currentSection,
            "name": section[5 : section.find("\n")],
            "section": section[:3],
            "previousSection": previous_section,
            "nextSection": next_section,
        }

        rule_from_previous_section = rule[0]

    # needs some reworking when actually used
    glossary = re.findall(r"^([^.\s\n][^.\n]*)\n((?:.+\n?)+)", comp_rules, re.MULTILINE)[:-1]
    for entry in glossary:
        glossary_json[entry[0].lower()] = {"term": entry[0], "definition": re.sub(r"\n$", "", entry[1])}

    with open(paths.structured_rules_dict, "w", encoding="utf-8") as output:
        output.write(json.dumps(rules_json, indent=4))

    return {"rules": rules_flattened, "keywords": keywords, "glossary": glossary_json, "toc": toc}


def extract_toc(comp_rules: str) -> list[ToCSection]:
    toc_start = re.search(r"^Contents", comp_rules, re.MULTILINE)
    toc_end = re.search(r"^Glossary", comp_rules, re.MULTILINE)

    toc_entries = re.findall(r"^(\d+)\. (.*)", comp_rules[toc_start.end() : toc_end.start()], re.MULTILINE)
    toc_sections = []
    current_section: ToCSection | None = None
    for number, title in toc_entries:
        if len(number) < 3:  # 1- (and in the future possibly 2-) digit number denotes a section
            if current_section:
                toc_sections.append(current_section)
            current_section = ToCSection(number=int(number), title=title, subsections=[])
        else:
            current_section.subsections.append(ToCSubsection(number=int(number), title=title))

    if current_section:
        toc_sections.append(current_section)
    return toc_sections


def split_ability_words(rules_text: str):
    splitter = re.compile(r", (?:and )?")
    trimmed = rules_text.rstrip(". ")
    list_str = re.findall(r"The ability words are (.*)", trimmed)[0]
    return splitter.split(list_str)


def split_keywords(title: str):
    """Sometimes one title contains multiple keywords ("Daybound and Nightbound"). We want to separate those."""
    return title.split(" and ")


if __name__ == "__main__":
    import sys

    extract(sys.argv[1])
