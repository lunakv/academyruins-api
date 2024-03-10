from dataclasses import dataclass

from src.difftool.diffsorter import CRDiffSorter, DiffSorter, MtrDiffSorter
from src.difftool.itemdiffer import CRItemDiffer, ItemDiffer, MtrItemDiffer, IpgItemDiffer
from src.difftool.matcher import CRMatcher, Matcher, MtrMatcher, IpgMatcher


@dataclass
class Diff:
    diff: list[(any, any)]  # list of changed item in a release
    moved: list[(str, str)]  # list of moved (but identical in content) items in a release


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
        moved = []
        for match_old, match_new in matches:
            old_item = old_doc.get(match_old)
            new_item = new_doc.get(match_new)
            diff = self.differ.diff_items(old_item, new_item)
            if diff:
                diffs.append({"old": diff[0], "new": diff[1]})
            elif match_old != match_new:
                moved.append((match_old, match_new))

        sorted_diffs = self.sorter.sort_diffs(diffs)
        sorted_moves = self.sorter.sort_moved(moved)
        return Diff(sorted_diffs, sorted_moves)


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


class IpgDiffMaker(DiffMaker):
    def __init__(self):
        super().__init__(IpgMatcher(), IpgItemDiffer(), MtrDiffSorter())

    def diff(self, old_doc, new_doc) -> Diff:
        return super().diff(MtrDiffMaker.key_by_title(old_doc), MtrDiffMaker.key_by_title(new_doc))
