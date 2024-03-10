import re

from src.extractor.pdf_common.paragraph_splitter import ParagraphSplitter

subheadings = [
    "Definition",
    "Examples",
    "Philosophy",
    "Additional Remedy",
    "Warning",
    "Game Loss",
    "Match Loss",
    "Disqualification",
]

subheading_regexps = [re.compile(r"^" + s + r"\s*$") for s in subheadings]


def is_subheading(line: str) -> bool:
    return any(sr.fullmatch(line) for sr in subheading_regexps)


class IpgParagraphSplitter(ParagraphSplitter):
    """Paragraph splitter that takes the subheadings of the IPG into account."""

    def __init__(self, content):
        super().__init__(content)

    def _is_new_paragraph(self, line: str) -> bool:
        if self.prev_line_empty and is_subheading(line):
            # a subheading creates its own paragraph
            return True
        if self.curr_paragraph and is_subheading(self.curr_paragraph):
            # the line after a subheading is also on a new paragraph
            return True
        return super()._is_new_paragraph(line)
