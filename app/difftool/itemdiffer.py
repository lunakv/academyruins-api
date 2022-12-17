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
        item = item.copy()
        item["content"] = content
        return item

    def diff_items(self, old_item, new_item) -> Union[None, tuple]:
        if not old_item:
            return None, new_item
        if not new_item:
            return new_item, None

        old_paragraphs = old_item["content"].split("\n\n")
        new_paragraphs = new_item["content"].split("\n\n")
        old_content = []
        new_content = []
        for para in old_paragraphs:
            old_content.extend(para.split(" "))
            old_content.append("\n\n")
        old_content.pop()
        for para in new_paragraphs:
            new_content.extend(para.split(" "))
            new_content.append("\n\n")
        new_content.pop()

        seq = difflib.SequenceMatcher(None, old_content, new_content)
        matches = seq.get_matching_blocks()

        diffed_old, diffed_new = [], []
        old_offset, new_offset = 0, 0
        for o, n, l in matches:
            block = old_content[old_offset:o]
            diffed_old.extend(self._wrap_change(block))
            block = new_content[new_offset:n]
            diffed_new.extend(self._wrap_change(block))

            diffed_old.extend(old_content[o : o + l])
            diffed_new.extend(new_content[n : n + l])
            old_offset = o + l
            new_offset = n + l

        return self._format(old_item, " ".join(diffed_old)), self._format(new_item, " ".join(diffed_new))
