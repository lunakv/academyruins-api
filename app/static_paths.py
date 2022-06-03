import os

__dir = os.path.dirname(__file__)
__gen = __dir + '/static/generated'
rules_dict = __gen + '/cr-flattened.json'
keyword_dict = __gen + '/keyword-dict.json'
glossary_dict = __gen + '/glossary.json'
structured_rules_dict = __gen + '/cr-structured.json'
unofficial_glossary_dict = __dir + '/static/unofficial-glossary.json'
redirects = __gen + '/redirects.json'
cr_dir = __gen + '/cr'
current_cr = cr_dir + '/cr-current.txt'
