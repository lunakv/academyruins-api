"""
Utility functions for cleaning up the converted PDF text before parsing.
"""
import re
from typing import Callable


def remove_page_nums(content: str) -> str:
    """The parsed PDF includes page numbers at the bottom of each "page". This removes those."""
    # a page number is 2+ blank lines, followed by a line with just a number, followed by 2+ blank lines
    page_num = re.compile(r"^(\s*\n){2,}\d+(\s*\n){2,}", re.MULTILINE)
    return page_num.sub("\n", content)


def trim_content(content, start_regex: re.Pattern, end_regex: re.Pattern) -> str:
    """Reduces the parsed PDF to only the part we care about (throws out ToC, appendices, etc.) based on regexes."""
    start_index = start_regex.search(content).start()
    end_index = end_regex.search(content).start()
    return content[start_index:end_index]


def remove_url_endblocks(content: str) -> str:
    """Remove the 'blocks' of URLs that tika sometimes places at the ends of pages or sections"""
    url_endblock_regex = re.compile(r"\n *\n(https?://\S+ *\n?)+(?=$|\n)")
    return url_endblock_regex.sub("\n", content)


def build(jobs: list[Callable[[str], str]]) -> Callable[[str], str]:
    def runner(content: str) -> str:
        for job in jobs:
            content = job(content)
        return content

    return runner
