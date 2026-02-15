import os

__dir = os.path.dirname(__file__)
__gen = os.path.join(__dir, "generated")
keyword_dict = os.path.join(__gen, "keyword-dict.json")
glossary_dict = os.path.join(__gen, "glossary.json")
structured_rules_dict = os.path.join(__gen, "cr-structured.json")
unofficial_glossary_dict = os.path.join(__dir, "unofficial-glossary.json")

_src_dir = os.path.dirname(__dir)
docs_dir = os.path.join(_src_dir, "static", "raw_docs")
cr_dir = os.path.join(docs_dir, "cr")
mtr_dir = os.path.join(docs_dir, "mtr")
ipg_dir = os.path.join(docs_dir, "ipg")
current_cr = os.path.join(cr_dir, "cr-current.txt")
