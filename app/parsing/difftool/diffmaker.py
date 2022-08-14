from .differ import Differ, CRDiffer
from .diffsorter import DiffSorter, CRDiffSorter
from .matcher import Matcher, CRMatcher


class DiffMaker:
    def __init__(self, matcher: Matcher, differ: Differ, sorter: DiffSorter):
        self.differ = differ
        self.matcher = matcher
        self.sorter = sorter

    def diff(self, old_doc, new_doc) -> list:
        old = old_doc
        new = new_doc
        matches = self.matcher.align_matches(old, new)
        diff = self.differ.create_diff(old, new, matches)
        return self.sorter.sort(diff)


class CRDiffMaker(DiffMaker):
    def __init__(self):
        super().__init__(CRMatcher(), CRDiffer(), CRDiffSorter())
