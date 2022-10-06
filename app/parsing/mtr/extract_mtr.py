import json
import os
import re
from dataclasses import asdict
from pathlib import Path

from dotenv import load_dotenv
from tika import parser

from app.utils.models import MtrSubsection, MtrAuxiliarySection, MtrNumberedSection


class ParagraphSplitter:
    """
    The parsed PDF uses linebreaks to fit the content to page width, sometimes even arbitrarily inserting a blank
    line. This class takes a chunk of the parsed text and converts it to a list of actual paragraphs.
    """

    url_line_regex = re.compile(r"^https?://\S+\s*$")

    def __init__(self, content):
        self.content = content
        self.paragraphs = []
        self.prev_line_empty = False
        self.curr_paragraph = None
        self.open_parens = 0

    def make_paragraphs(self):
        lines: list[str] = self.content.split("\n")
        for line in lines:
            if self.url_line_regex.fullmatch(line):
                # tika parses hyperlinks and prints them on separate lines. ignore those
                continue
            if not line or line.isspace():
                # a new paragraph can only start after a blank line, otherwise it's just split to fit in page width
                self.prev_line_empty = True
                continue

            line = line.strip()
            if self.curr_paragraph is None:
                self.curr_paragraph = line
            elif self._is_new_paragraph(line):
                self.paragraphs.append(self.curr_paragraph)
                self.curr_paragraph = line
            else:
                separator = "\n" if self._is_list_item(line) else " "
                self.curr_paragraph += separator + line
            self.prev_line_empty = False
            self._update_parens(line)

        self.paragraphs.append(self.curr_paragraph)

    def _is_new_paragraph(self, line: str) -> bool:
        if not self.prev_line_empty or self.open_parens > 0:
            return False
        if len(line) < 5:
            return False
        if self._is_list_item(line):
            return False
        if line[0].islower():
            return False
        return True

    def _update_parens(self, line: str) -> None:
        for char in line:
            if char == "(":
                self.open_parens += 1
            elif char == ")" and self.open_parens > 0:
                self.open_parens -= 1

    def _is_list_item(self, line: str) -> bool:
        return line.startswith("•") or (re.match(r"^\d+\. ", line))


def trim_content(content):
    """Reduces the parsed PDF to only the part we care about (throws out ToC, appendices, etc.)"""
    start_index = re.search(r"^Introduction\s*$", content, re.MULTILINE).start()
    end_index = re.search(r"^Appendix [A-Z]—[a-zA-Z ]*$", content, re.MULTILINE).start()
    return content[start_index:end_index]


def remove_page_nums(content: str) -> str:
    """The parsed PDF includes page numbers at the bottom of each "page". This removes those."""
    # a page number is 2+ blank lines, followed by a line with just a number, followed by 2+ blank lines
    page_num = re.compile(r"^(\s*\n){2,}\d+(\s*\n){2,}", re.MULTILINE)
    return page_num.sub("\n", content)


def is_actual_header(section: int, subsection: int, prev: MtrSubsection) -> bool:
    # a simple test - header must follow immediately after the previous confirmed header
    # we could parse the ToC for more robust results, but this is sufficient for now
    return (section == prev.section + 1 and subsection == 0) or (
        section == prev.section and subsection == prev.subsection + 1
    )


def get_chunk_content(chunk_start: int, chunk_end: int, content: str) -> str:
    # content starts at the next line after the header
    start = content.find("\n", chunk_start)
    return content[start:chunk_end].strip()


def split_into_chunks(content: str) -> [MtrSubsection]:
    """ "Separates the parsed MTR into a list of sections and subsections"""
    chunks = []
    open_chunk = MtrSubsection(0, 0, "Introduction", "")
    chunk_start = 0

    potential_header_lines = re.compile(r"^(\d+)\.(\d+)? +([a-zA-Z /-]+)$", re.MULTILINE)
    for match in potential_header_lines.finditer(content):
        section = int(match.group(1))
        subsection = int(match.group(2) or 0)
        title = match.group(3).strip()

        if is_actual_header(section, subsection, open_chunk):
            open_chunk.content = get_chunk_content(chunk_start, match.start(), content)
            chunks.append(open_chunk)
            open_chunk = MtrSubsection(section, subsection, title, "")
            chunk_start = match.start()

    open_chunk.content = get_chunk_content(chunk_start, len(content), content)
    chunks.append(open_chunk)
    return chunks


def build_structure(chunks: [MtrSubsection]):
    section_by_num = {}
    sections = []
    for chunk in chunks:
        if chunk.section == 0:
            sections.append(MtrAuxiliarySection(chunk.title, chunk.content))

        elif chunk.subsection == 0:
            new_section = MtrNumberedSection(chunk.section, chunk.title, [])
            sections.append(new_section)
            section_by_num[chunk.section] = new_section
        else:
            section = section_by_num[chunk.section]
            section.subsections.append(chunk)
    return sections


def extract(filepath: Path | str) -> [dict]:
    if os.environ.get("USE_TIKA") != "1":
        return None

    args = [str(filepath)]
    tika_server = os.environ.get("TIKA_URL")
    if tika_server:
        args.append(tika_server)

    content = parser.from_file(*args)["content"]
    content = remove_page_nums(trim_content(content))
    chunks = split_into_chunks(content)

    for chunk in chunks:
        if chunk.section == 0 or chunk.subsection != 0:
            cleaner = ParagraphSplitter(chunk.content)
            cleaner.make_paragraphs()
            chunk.content = "\n\n".join(cleaner.paragraphs)

    sections = build_structure(chunks)

    return [asdict(s) for s in sections]


if __name__ == "__main__":
    load_dotenv("/home/vaasa/rules-api/.env")
    parsed = extract("./in.pdf")
    with open("./out.json", "w") as file:
        json.dump(parsed, file)
