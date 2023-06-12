import re
from abc import ABC, abstractmethod


class DiffSorter(ABC):
    """
    Policy class that handles how a specified list of diffs is sorted.
    """

    @abstractmethod
    def diff_to_sort_key(self, item) -> int:
        """
        Method for calculating the sort key of a given diff item
        """
        pass

    @abstractmethod
    def move_to_sort_key(self, key: tuple[str, str]) -> int | str:
        """
        Method for calculating the sort key of a given move item
        """
        pass

    def sort_diffs(self, diffs: list) -> list:
        return sorted(diffs, key=self.diff_to_sort_key)

    def sort_moved(self, moved: list[tuple[str, str]]) -> list[tuple[str, str]]:
        return sorted(moved, key=self.move_to_sort_key)


class CRDiffSorter(DiffSorter):
    """
    DiffSorter specification designed to sort CR diffs in ascending order
    """

    @staticmethod
    def rule_num_to_sort_key(num: str) -> int:
        """
        Converts rule number to an integer sort key.

        The sort can't be simply lexicographic, as e.g. 701.10 has to go after 701.2.
        This method calculates the key by splitting the number into its three component parts (rule, subrule and letter)
        and then creates a weighted sum of all those parts.
        """
        rule_num_regex = r"(\d{3})\.(\d+)([a-z]?)"
        num_split = re.match(rule_num_regex, num)
        rule = num_split.group(1)
        subrule = num_split.group(2)
        letter = num_split.group(3)
        letter_val = ord(letter) - ord("a") + 1 if letter else 0  # '' -> 0, 'a' -> 1, 'b' -> 2, ...

        # rules only go to 9xx, 1000 multiplier is enough. letters only go 1-27, so 100 multiplier is enough there too
        return int(rule) * 100_000 + int(subrule) * 100 + letter_val

    def diff_to_sort_key(self, item) -> int:
        # the diff rows are sorted primarily by the new rule, the old rule number only being used for deletions
        sort_by = item["new"] or item["old"]
        return CRDiffSorter.rule_num_to_sort_key(sort_by["ruleNum"])

    def move_to_sort_key(self, item: tuple[str, str]) -> int:
        return CRDiffSorter.rule_num_to_sort_key(item[1])


class MtrDiffSorter(DiffSorter):
    def diff_to_sort_key(self, item: dict) -> int:
        comparison_source = item.get("new") or item.get("old") or {}
        s = comparison_source.get("section") or 0
        ss = comparison_source.get("subsection") or 0
        return s * 100 + ss

    def move_to_sort_key(self, key: tuple[str, str]) -> str:
        return key[1]
