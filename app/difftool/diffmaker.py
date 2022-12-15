from dataclasses import dataclass

from .diffsorter import CRDiffSorter, DiffSorter, MtrDiffSorter
from .itemdiffer import CRItemDiffer, ItemDiffer, MtrItemDiffer
from .matcher import CRMatcher, Matcher, MtrMatcher


@dataclass
class Diff:
    diff: list[(any, any)]
    matches: list[(str, str)]


class DiffMaker:
    """
    Main class for creating a diff between two versions of a document.
    """

    def __init__(self, matcher: Matcher, differ: ItemDiffer, sorter: DiffSorter):
        self.differ = differ
        self.matcher = matcher
        self.sorter = sorter

    def diff(self, old_doc, new_doc) -> Diff:
        """
        Returns the list of diffs between old_doc and new_doc.
        """
        matches = self.matcher.align_matches(old_doc, new_doc)
        diffs = []
        for match_old, match_new in matches:
            old_item = old_doc.get(match_old)
            new_item = new_doc.get(match_new)
            diff = self.differ.diff_items(old_item, new_item)
            if diff:
                diffs.append({"old": diff[0], "new": diff[1]})

        sorted = self.sorter.sort(diffs)
        return Diff(sorted, matches)


class CRDiffMaker(DiffMaker):
    def __init__(self, forced_matches=None):
        super().__init__(CRMatcher(forced_matches), CRItemDiffer(), CRDiffSorter())


class MtrDiffMaker(DiffMaker):
    @staticmethod
    def key_by_title(items: list[dict]) -> dict[str, dict]:
        keyed = {}
        for chunk in items:
            keyed[chunk["title"]] = chunk

        return keyed

    def __init__(self):
        super().__init__(MtrMatcher(), MtrItemDiffer(), MtrDiffSorter())

    def diff(self, old_doc, new_doc) -> Diff:
        return super().diff(MtrDiffMaker.key_by_title(old_doc), MtrDiffMaker.key_by_title(new_doc))
