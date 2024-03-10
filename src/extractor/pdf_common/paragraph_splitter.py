import re
from typing import Literal


class ParagraphSplitter:
    """
    The parsed PDF uses linebreaks to fit the content to page width, sometimes even arbitrarily inserting a blank
    line. This class takes a chunk of the parsed text and converts it to a list of actual paragraphs.
    """

    hyphenated_end_regex = re.compile(r"\w([-–—])$")

    def __init__(self, content):
        self.content = content
        self.paragraphs = []
        self.prev_line_empty = False
        self.curr_paragraph = None
        self.open_parens = 0
        self.list_type = None

    def make_paragraphs(self):
        # tika places URLs of parsed hyperlinks at the end of each section. Remove those.
        lines: list[str] = self.content.split("\n")

        for line in lines:
            if not line or line.isspace():
                # a new paragraph can only start after a blank line, otherwise it's just split to fit in page width
                self.prev_line_empty = True
                continue

            line = line.strip()
            if self._is_new_paragraph(line):
                if self.curr_paragraph:
                    self._append_current_paragraph()
                self.curr_paragraph = line
                self._update_list_type(line)
            else:
                separator = " "
                if self._is_list_item(line):
                    # list items are on separate lines
                    separator = "\n"
                elif self.hyphenated_end_regex.search(self.curr_paragraph):
                    # hyphenated words split by a line break shouldn't have a space after the hyphen
                    separator = ""
                self.curr_paragraph += separator + line
            self.prev_line_empty = False
            self._update_parens(line)

        self._append_current_paragraph()

    def _is_new_paragraph(self, line: str) -> bool:
        """A heuristic to determine if a line starts a new paragraph or just continues the current one"""
        if self.curr_paragraph is None:
            # only true for the first line of a section, which always begins a new paragraph
            return True
        if self._curr_paragraph_ends_with_article():
            # if the previous line ends with an article, then the following line must be a continuation
            # this is kind of a hack to avoid a list being split into paragraphs by a weirdly-parsed multi-line item,
            # and it could (should?) be replaced with better list detection.
            return False
        if self._is_list_item(line):
            # paragraph cannot start in the middle of a bulleted list (nor a list immediately after another list)
            return not self.list_type
        if not self.prev_line_empty or self.open_parens > 0:
            # paragraph has to start after an empty line and cannot start inside parentheses
            return False
        if len(line) < 5:
            # a very short line is a parsing artifact and cannot be the beginning of a paragraph
            return False
        if not line[0].isupper():
            # paragraphs always start with a new sentence (and therefore a capital letter)
            return False
        if self.list_type and len(line.split(" ")) < 4 and line.rstrip()[-1] == ".":
            # sometimes the last PDF line of a list item sentence can begin with a capital letter
            # see the list in 7.2: Card Use in Limited Tournaments
            return False
        return True

    def _update_parens(self, line: str) -> None:
        for char in line:
            if char == "(":
                self.open_parens += 1
            elif char == ")" and self.open_parens > 0:
                self.open_parens -= 1

    def _update_list_type(self, line: str) -> None:
        self.list_type = self._get_list_type(line)

    @staticmethod
    def _get_list_type(line: str) -> Literal["bullet", "number", "letter"] | None:
        """Determines what kind of list (if any) a line belongs into"""
        if line.startswith("•"):
            return "bullet"
        if re.match(r"^\d+\. ", line):
            return "number"
        if re.match(r"^[A-Z]\. ", line):
            return "letter"
        return None

    def _is_list_item(self, line: str) -> bool:
        list_type = self._get_list_type(line)
        if not list_type:
            return False
        # two lists of different types don't follow right after each other
        return not self.list_type or list_type == self.list_type

    def _append_current_paragraph(self) -> None:
        # sometimes a bulleted list ends with a lone bullet point, which doesn't have any semantic value
        # and is just a formatting artifact, so we remove it (this tends to happen in 6.x lists)
        self.curr_paragraph = re.sub(r"\n\u2022 *$", "", self.curr_paragraph)
        self.paragraphs.append(self.curr_paragraph)

    def _curr_paragraph_ends_with_article(self) -> bool:
        return self.curr_paragraph.endswith(" a") or self.curr_paragraph.endswith(" the")
