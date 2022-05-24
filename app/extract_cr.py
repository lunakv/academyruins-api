import json
import re
import static_paths as paths

keyword_regex = r'702.(?:[2-9]|\d\d+)'
keyword_action_regex = r'701.(?:[2-9]|\d\d+)'
ability_words_rule = '207.2c'

# parse plaintext CR into structured representations
# lifted directly from an old VensersJournal file, should be cleaned up at some point
def extract(rules_file):
    rules_json = {}
    rules_flattened = {}
    glossary_json, examples_json = {}, []

    def split_ability_words(rules_text):
        splitter = re.compile(r', (?:and )?')
        list_str = re.findall(r'The ability words are (.*)', rules_text)[0]
        return splitter.split(list_str)


    with open(rules_file, 'r', encoding='utf-8') as comp_rules:
        comp_rules = comp_rules.read()

        start_index = comp_rules.find('Glossary')
        comp_rules = comp_rules[start_index:]

        comp_rules = comp_rules.replace("“", "\"")
        comp_rules = comp_rules.replace("”", "\"")
        comp_rules = comp_rules.replace("’", "'")
        comp_rules = comp_rules.replace("‘", "'")
        comp_rules = comp_rules.replace("—", "-")
        comp_rules = re.sub(r"(\w)–—(\w)", r"\1—\2", comp_rules)
        comp_rules = comp_rules.replace("(tm)", "™")
        comp_rules = comp_rules.replace("(r)", "®")
        comp_rules = re.sub(r"\n\s{4,}(\w)", r" \1", comp_rules)

        sections = re.findall(r'^\d{3}\..*?(?=^\d{3}\. |Glossary)',
                            comp_rules,
                            re.MULTILINE | re.DOTALL)

        rule_from_previous_section = ""
        rule_object_ref = {}
        keywords = {
            'keywordAbilities': [ ],
            'keywordActions': [ ],
            'abilityWords': [ ],
        }
       

        for index, section in enumerate(sections):
            print(index, section[:3])
            currentSection = []
            rules = re.findall('^(\d{3}\.[^\s.]{1,4})[\s.]*(.*)'
                            '(?:\nExample: (.*))?(?:\nExample: (.*))?'
                            '(?:\nExample: (.*))?(?:\nExample: (.*))?',
                            section,
                            re.MULTILINE)
            for idx, rule in enumerate(rules):
                nonempty_examples = []
                for ex in rule[2:5]:
                    if ex != '':
                        nonempty_examples.append(ex)
                if len(nonempty_examples) == 0:
                    nonempty_examples = None
                new_example = {'examples': nonempty_examples,
                            'ruleNumber': rule[0]}

                previous_rule = ""
                next_rule = ""

                if idx-1 < 0:
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
                    if not rule_object_ref[rule_from_previous_section.split('.')[1]]['navigation']['nextRule']:
                        rule_object_ref[rule_from_previous_section.split('.')[1]]['navigation']['nextRule'] = rule[0]
                except (KeyError, IndexError) as e:
                    pass
                new_rule = {'ruleNumber': rule[0],
                            'fragment': rule[0].split('.')[1],
                            'ruleText': rule[1],
                            'examples': nonempty_examples,
                            'navigation': {'previousRule': previous_rule,
                                        'nextRule': next_rule}}
                currentSection.append(new_rule)
                rules_flattened[new_rule['ruleNumber']] = new_rule
                rule_object_ref = new_rule
                if re.fullmatch(keyword_regex, new_rule['ruleNumber']):
                    keywords['keywordAbilities'].append(new_rule['ruleText'])
                elif re.fullmatch(keyword_action_regex, new_rule['ruleNumber']):
                    keywords['keywordActions'].append(new_rule['ruleText'])
                elif new_rule['ruleNumber'] == ability_words_rule:
                    keywords['abilityWords'] = split_ability_words(new_rule['ruleText'])

            previous_section = None
            next_section = None

            if index-1 < 0:
                pass
            else:
                prev = sections[index - 1]
                previous_section = {}
                previous_section['name'] = prev[:prev.find('\n')]
                previous_section['id'] = prev[:3]
            try:
                next = sections[index + 1]
                next_section = {}
                next_section['name'] = next[:next.find('\n')]
                next_section['id'] = next[:3]
            except IndexError:
                pass
            rules_json[section[:3]] = {'rules': currentSection,
                                    'name': section[5:section.find('\n')],
                                    'section': section[:3],
                                    'previousSection': previous_section,
                                    'nextSection': next_section }

            rule_from_previous_section = rule[0]

        # needs some reworking when actually used
        glossary = re.findall('^([^.\s\n][^.\n]*)\n((?:.+\n?)+)',
                comp_rules, re.MULTILINE)[:-1]
        for entry in glossary:
            glossary_json[entry[0].lower()] = re.sub(r'\n$', '', entry[1])
            

        with open('./static/cr-structured.json', 'w', encoding='utf-8') as output:
            output.write(json.dumps(rules_json, indent = 4))
        
        with open(paths.rules_dict, 'w', encoding='utf-8') as output:
            output.write(json.dumps(rules_flattened, indent = 4))

        with open(paths.keyword_dict, 'w', encoding='utf-8') as output:
            output.write(json.dumps(keywords, indent = 4))

        with open(paths.glossary_dict, 'w', encoding='utf-8') as output:
            output.write(json.dumps(glossary_json, indent = 4))

if __name__ == '__main__':
    import sys
    extract(sys.argv[1])
