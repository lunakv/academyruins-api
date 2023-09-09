import os

__dir = os.path.dirname(__file__)
__gen = __dir + "/generated"
keyword_dict = __gen + "/keyword-dict.json"
glossary_dict = __gen + "/glossary.json"
structured_rules_dict = __gen + "/cr-structured.json"
unofficial_glossary_dict = __dir + "/unofficial-glossary.json"

docs_dir = "src/static/raw_docs"
cr_dir = "src/static/raw_docs/cr"
current_cr = cr_dir + "/cr-current.txt"
