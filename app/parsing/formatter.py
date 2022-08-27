import re
from abc import ABC, abstractmethod

"""
WotC is pretty good about typography in their CR files. However, sometimes they mess things up. Most notably,
the RNA file has all the usual typographical niceties removed, which creates large nonsensical diffs around it.
These classes create a structure that allows me to automatically reformat these offending files as they're parsed.
"""


class CRFormatter(ABC):
    @abstractmethod
    def format(self, file: str) -> str:
        pass


class EmptyCRFormatter(CRFormatter):
    def format(self, file: str) -> str:
        return file


class RnaCRFormatter(CRFormatter):
    def format(self, file: str) -> str:
        # quotation mark replacements
        file = file.replace(' "', " “")
        file = file.replace('("', "(“")
        file = file.replace('"', "”")
        file = file.replace("'", "’")
        file = file.replace(" ’", " ‘")
        # copyright symbols
        file = file.replace("(tm)", "™")
        file = file.replace("(r)", "®")
        # replacing hyphens -- this part is tailored to the exact incorrect rules
        file = file.replace("}-[", "}—[")
        file = re.sub(r"(\d\w)-(\w)", r"\1–\2", file)  # sub-rule range
        file = re.sub(r"(\d)-(\d)", r"\1–\2", file)  # number range
        file = re.sub(  # type line
            r"(Artifact|Creature|Enchantment|Planeswalker|Instant|Sorcery|Plane) -", r"\1 —", file
        )
        file = file.replace("-[cost]", "—[cost]")  # ability words
        file = re.sub(  # other random rules that needed to be corrected
            r"-(they|for|Conspiracy™|even|either|in|or|chooses|not|whose|the|unless|read|that|any|.”) ",
            r"—\1 ",
            file,
        )
        file = file.replace("- [", "— [")

        # reverting overcorrections
        file = re.sub(r"(phased|fill)—in", r"\1-in", file)
        # technically correct with an en dash, but all the surrounding versions also have a hyphen, so we keep it there
        file = file.replace("601.2g–h", "601.2g-h")
        return file


class CRFormatterFactory:
    @staticmethod
    def create_formatter(set_code: str | None = None) -> CRFormatter:
        if set_code == "RNA":
            return RnaCRFormatter()
        return EmptyCRFormatter()
