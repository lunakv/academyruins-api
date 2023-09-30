import difflib
import re
from abc import ABC, abstractmethod
from typing import Union


class ItemDiffer(ABC):
    """
    Class for diffing individual items of a document.
    """

    DIFF_START_MARKER = "<<<<"
    DIFF_END_MARKER = ">>>>"

    def _wrap_change(self, rule_slice: list[str]) -> list[str]:
        """
        Inserts diff markers around a list of words
        """
        if not rule_slice:
            return []
        rule_slice[0] = self.DIFF_START_MARKER + rule_slice[0]
        rule_slice[-1] += self.DIFF_END_MARKER
        return rule_slice

    @abstractmethod
    def diff_items(self, old_item, new_item) -> Union[None, tuple]:
        """
        Given two matched versions of a document item, produces a tuple of diffs of those versions.
        Returns None if both versions are identical.
        """
        pass


class CRItemDiffer(ItemDiffer):
    def _format_item(self, number: str, text: str) -> dict:
        return {"ruleNum": number, "ruleText": text}

    def _is_change(self, rule_slice: list[str]) -> (list[str], bool):
        """
        Check that the marked block is actually a change of something other than rule renumbering.
        """
        # matches a mention of a rule number / range of numbers
        # TODO actually inspect how this regex works
        if not rule_slice:
            return False
        rule_mention_regex = r"^(?:rules? )?\d{3}(?:\.\d+[a-z]*)*(?:–\d{3}(?:\.\d+[a-z]?)?)?\)?[.,]?\)?"
        return not re.fullmatch(rule_mention_regex, " ".join(rule_slice))

    def diff_items(self, old_item, new_item) -> Union[None, tuple]:
        old_rule_num = old_item and old_item["ruleNumber"]
        new_rule_num = new_item and new_item["ruleNumber"]
        old_rule_text = old_item and old_item["ruleText"].strip()
        new_rule_text = new_item and new_item["ruleText"].strip()

        if not old_item:
            return None, self._format_item(new_rule_num, new_rule_text)
        if not new_item:
            return self._format_item(old_rule_num, old_rule_text), None

        if old_rule_text == new_rule_text:
            # The rule just changed numbers, but the text is the exact same
            return None

        # we want to diff on whole words, not individual characters
        old_text = old_rule_text.split(" ")
        new_text = new_rule_text.split(" ")

        seq = difflib.SequenceMatcher(None, old_text, new_text)
        matches = seq.get_matching_blocks()

        diffed_old, diffed_new = [], []
        old_offset, new_offset = 0, 0
        changed = False
        # get_matching block produces a list of triplets such that old_text[o:o+l] == new_text[n:n+l]
        # the parts we want to diff are between these blocks, i.e. o1+l to o2 (n1+l to n2)
        # this loop goes through these triplets, adding each matched block unchanged and the rest wrapped with diff tags
        for o, n, l in matches:
            block = old_text[old_offset:o]
            if self._is_change(block):
                block = self._wrap_change(block)
                changed = True
            diffed_old.extend(block)

            block = new_text[new_offset:n]
            if self._is_change(block):
                block = self._wrap_change(block)
                changed = True
            diffed_new.extend(block)

            diffed_old.extend(old_text[o : o + l])
            diffed_new.extend(new_text[n : n + l])
            old_offset = o + l
            new_offset = n + l

        if not changed:
            # it's possible the only changes were due to rules renumbering, which we don't count
            return None

        return (
            self._format_item(old_rule_num, " ".join(diffed_old)),
            self._format_item(new_rule_num, " ".join(diffed_new)),
        )


class MtrItemDiffer(ItemDiffer):
    def _format(self, item, content):
        """Turns a list of diffed paragraphs into an actual diff item"""
        joined = "\n\n".join(content)
        item = item.copy()
        item["content"] = joined
        return item

    @staticmethod
    def _split_paragraph(paragraph: str) -> [str]:
        """Splits a paragraph into individual blocks to be fed into the sequence matcher"""
        return re.split(r"(\W)", paragraph)

    def _diff_paragraph(self, old_para: str, new_para: str) -> (str, str):
        """Produces a diff of one pair of paragraphs"""

        # we don't want diffs starting in the middle of a word - split the input into word/non-word chunks
        old_split = self._split_paragraph(old_para)
        new_split = self._split_paragraph(new_para)

        seq = difflib.SequenceMatcher(lambda x: x == " ", old_split, new_split, autojunk=False)
        matches = seq.get_matching_blocks()

        diffed_old, diffed_new = [], []
        old_offset, new_offset = 0, 0
        # go through the matching blocks
        for o, n, l in matches:
            # add everything between the last match and this one, marked as changed
            block = old_split[old_offset:o]
            diffed_old.extend(self._wrap_change(block))
            block = new_split[new_offset:n]
            diffed_new.extend(self._wrap_change(block))

            # add this match, as is
            diffed_old.extend(old_split[o : o + l])
            diffed_new.extend(new_split[n : n + l])
            old_offset = o + l
            new_offset = n + l

        return "".join(diffed_old), "".join(diffed_new)

    @staticmethod
    def _find_paragraph_match(old_para: str, new_paragraphs: list[str]) -> str | None:
        prefix_suffix_match_length = min(30, len(old_para))
        best_match = difflib.get_close_matches(old_para, new_paragraphs, n=1, cutoff=0.4)
        if not best_match:
            best_match = [x for x in new_paragraphs if x.startswith(old_para[:prefix_suffix_match_length])]
        if not best_match:
            best_match = [x for x in new_paragraphs if x.endswith(old_para[-prefix_suffix_match_length:])]
        return best_match[0] if best_match else None

    def diff_items(self, old_item: dict | None, new_item: dict | None) -> None | tuple[dict | None, dict | None]:
        if not old_item:
            return None, new_item
        if not new_item:
            return new_item, None

        if old_item["content"] == new_item["content"] and old_item["title"] == new_item["title"]:
            # section was just renumbered without any actual changes
            return None

        # We don't want the change blocks to span multiple paragraphs, so we pair the paragraphs up and diff them 1 by 1
        old_paragraphs = old_item["content"].split("\n\n")
        new_paragraphs = new_item["content"].split("\n\n")

        diffed_old_paras = []
        diffed_new_paras = []

        new_match_start = 0
        for old_index, old_para in enumerate(old_paragraphs):
            # for each old paragraph, we find its closest match among the new paragraphs in this section
            # we start the search only after the last match to avoid two matched pairs "crossing"
            best_match = self._find_paragraph_match(old_para, new_paragraphs[new_match_start:])
            if best_match:
                # add all new paragraphs between the last match and this one, marked as newly added
                new_index = new_paragraphs.index(best_match)
                for i in range(new_match_start, new_index):
                    diffed_new_paras.extend(self._wrap_change([new_paragraphs[i]]))
                new_match_start = new_index + 1

                # diff the matched paragraphs and add the result to both sides
                para_diffed_old, para_diffed_new = self._diff_paragraph(old_para, best_match)
                diffed_old_paras.append(para_diffed_old)
                diffed_new_paras.append(para_diffed_new)
            else:
                # if an old paragraph doesn't have a match, it's deleted
                diffed_old_paras.extend(self._wrap_change([old_para]))

        # finally, add all the remaining unmatched new paragraphs marked as added
        for i in range(new_match_start, len(new_paragraphs)):
            diffed_new_paras.extend(self._wrap_change([new_paragraphs[i]]))

        return self._format(old_item, diffed_old_paras), self._format(new_item, diffed_new_paras)
