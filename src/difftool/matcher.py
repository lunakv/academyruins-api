import difflib
from abc import ABC, abstractmethod

from .matchscoregraph import MatchScoreGraph


class Matcher(ABC):
    """
    Class for aligning old versions of document items with their most likely new counterparts.
    """

    def __init__(self, forced_matches=None):
        if forced_matches is None:
            forced_matches = []
        self.forced = forced_matches

    @abstractmethod
    def align_matches(self, old, new) -> list[tuple]:
        pass


class CRMatcher(Matcher):
    """
    Matcher variant for aligning CR entries
    """

    def prune_identical_rules(self, old, new):
        """
        Delete rules that have the same rule number and identical rules text.
        Such rules don't need to be considered in the diff.
        """
        to_purge = []
        for num in old:
            if num in new and old[num]["ruleText"] == new[num]["ruleText"]:
                to_purge.append(num)

        for num in to_purge:
            del old[num]
            del new[num]

    def align_matches(self, old, new) -> list[tuple[any, any]]:
        """
        Finds likely pairings between two CR versions.

        After removing all the obviously identical rules, the method finds the closest fuzzy matches for each old
        rule and creates a weighted bipartite graph based on the quality of the match (partitions are the old and new
        rules, edges are weighed by how alike two rules/vertices are). Once this graph is constructed, the overall
        maximum edge (the most likely match) is successively removed along with its two vertices. Once the graph has no
        edges, all remaining rules are without a partner and are marked as additions/deletions .
        """
        matched_pairs = []

        old_unmatched = old.copy()  # old rules that don't yet have a match
        new_unmatched = new.copy()  # new rules that don't yet have a match

        for match in self.forced:
            if match[0]:
                del old_unmatched[match[0]]
            if match[1]:
                del new_unmatched[match[1]]
            matched_pairs.append(match)

        self.prune_identical_rules(old_unmatched, new_unmatched)
        new_unmatched_texts = [item["ruleText"] for item in new_unmatched.values()]

        score_graph = MatchScoreGraph()

        # find best matches for each word and add them to the graph
        for old_num in old_unmatched:
            # we compare similarity based on whole words, not individual chars
            old_text = old_unmatched[old_num]["ruleText"].split(" ")
            split_new_texts = [x.split(" ") for x in new_unmatched_texts]
            best_matches = difflib.get_close_matches(old_text, split_new_texts, cutoff=0.4)
            for match in best_matches:
                # TODO better way to handle identically worded rules?
                match_items = list(filter(lambda val: val["ruleText"] == " ".join(match), new_unmatched.values()))
                for item in match_items:
                    new_num = item["ruleNumber"]
                    score = difflib.SequenceMatcher(None, match, old_text).ratio()
                    score_graph.add_edge(new_num, old_num, score)

        # pair old and new rules based on the graph edges
        while score_graph.edge_count > 0:
            new_num, old_num, weight = score_graph.get_max_edge()
            matched_pairs.append((old_num, new_num))
            del old_unmatched[old_num]
            del new_unmatched[new_num]
            score_graph.remove_nodes(new_num, old_num)

        # add the rest as unpaired
        for old in old_unmatched:
            matched_pairs.append((old, None))
        for new in new_unmatched:
            matched_pairs.append((None, new))
        return matched_pairs


class MtrMatcher(Matcher):
    @staticmethod
    def prune_identical_rules(old, new):
        props = ["section", "subsection", "content"]
        to_prune = []
        for title in old:
            if title in new and all(old[title][prop] == new[title][prop] for prop in props):
                to_prune.append(title)

        for title in to_prune:
            del old[title]
            del new[title]

    @staticmethod
    def match_by_title(old, new) -> list[tuple]:
        pairs = []
        for title in old:
            if title in new:
                pairs.append((title, title))
                del new[title]
        for title, _ in pairs:
            del old[title]

        return pairs

    @staticmethod
    def match_by_number(old: dict, new: dict) -> list[tuple]:
        pairs = []
        for old_title, old_section in old.items():
            new_title = next(
                (
                    t
                    for t, v in new.items()
                    if v["section"] == old_section["section"] and v["subsection"] == old_section["subsection"]
                ),
                None,
            )

            if new_title:
                pairs.append((old_title, new_title))
                del new[new_title]

        for old_title, _ in pairs:
            del old[old_title]
        return pairs

    def align_matches(self, old, new) -> list[tuple]:
        old = old.copy()
        new = new.copy()

        self.prune_identical_rules(old, new)

        # Match primarily on title. If the versions have the same title, they're considered the same section
        matched_pairs = self.match_by_title(old, new)
        # If there are remaining sections that have the same number, they were probably just renamed.
        # (This assumption can break in certain condition, but let's cross that bridge when we get to it.)
        matched_pairs.extend(self.match_by_number(old, new))
        # The rest are just added/deleted sections
        matched_pairs.extend((title, None) for title in old)
        matched_pairs.extend((None, title) for title in new)

        return matched_pairs
