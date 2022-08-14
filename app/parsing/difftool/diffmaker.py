from .itemdiffer import ItemDiffer, CRItemDiffer
from .diffsorter import DiffSorter, CRDiffSorter
from .matcher import Matcher, CRMatcher


class DiffMaker:
    """
    Main class for creating a diff between two versions of a document.
    """

    def __init__(self, matcher: Matcher, differ: ItemDiffer, sorter: DiffSorter):
        self.differ = differ
        self.matcher = matcher
        self.sorter = sorter

    def diff(self, old_doc, new_doc) -> list:
        """
        Returns the list of diffs between old_doc and new_doc.
        """
        matches = self.matcher.align_matches(old_doc, new_doc)
        diffs = []
        for match_old, match_new in matches:
            old_item = old_doc[match_old] if match_old else None
            new_item = new_doc[match_new] if match_new else None
            diff = self.differ.diff_items(old_item, new_item)
            if diff:
                diffs.append({"old": diff[0], "new": diff[1]})

        return self.sorter.sort(diffs)


class CRDiffMaker(DiffMaker):
    """
    A variant of DiffMaker designed to diff the CR
    """

    def __init__(self):
        super().__init__(CRMatcher(), CRItemDiffer(), CRDiffSorter())
