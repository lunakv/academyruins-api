import re
from abc import ABC, abstractmethod


class DiffSorter(ABC):
    @abstractmethod
    def sort(self, diff: list) -> list:
        pass


class CRDiffSorter(DiffSorter):
    @staticmethod
    def num_to_key(num) -> int:
        rule_num_regex = r"(\d{3})\.(\d+)([a-z]?)"
        num_split = re.match(rule_num_regex, num)
        rule = num_split.group(1)
        subrule = num_split.group(2)
        letter = num_split.group(3)
        letter_val = ord(letter) - ord("a") + 1 if letter else 0
        return int(rule) * 100_000 + int(subrule) * 100 + letter_val

    @staticmethod
    def item_to_key(item) -> int:
        sort_by = item["new"] or item["old"]
        return CRDiffSorter.num_to_key(sort_by["ruleNum"])

    def sort(self, diff: list) -> list:
        return sorted(diff, key=CRDiffSorter.item_to_key)
