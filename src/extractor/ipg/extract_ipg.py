import datetime
import re
from pathlib import Path

from src.extractor.ipg.IpgParagraphSplitter import IpgParagraphSplitter
from src.extractor.pdf_common import converter, cleanup
from src.ipg.schemas import Penalty, IpgChunk


def uncapitalize(title: str) -> str:
    """Some titles are written in small caps, which gets parsed into all caps. This re-applies the normal casing."""
    if title == title.upper():
        # only operate on all caps titles
        title = title.title()
        # un-capitalize articles and prepositions (the list is based on the actual text and some personal additions)
        parts = re.split(r"(\s(?:A|The|Of|To|In)\b)", title)
        for i in range(1, len(parts), 2):
            parts[i] = parts[i].lower()
        title = "".join(parts)

    return title


def split_into_chunks(content: str) -> [IpgChunk]:
    chunks = []
    # First create the unnumbered chunks (Introduction and Framework of this Document)
    framework_match = re.search(r"^FRAMEWORK OF THIS DOCUMENT\s*$", content, re.MULTILINE)
    intro_content = converter.get_chunk_content(0, framework_match.start(), content)
    intro_chunk = IpgChunk(section=None, subsection=None, title="Introduction", penalty=None, content=intro_content)
    chunks.append(intro_chunk)

    open_chunk = IpgChunk(section=None, subsection=None, title="Framework of this Document", penalty=None, content=None)
    chunk_start = framework_match.start()

    # Then, create the numbered chunks
    penalty_regexp = "|".join(Penalty)
    potential_header_lines = re.compile(
        r"^(\d+)\.(?:(\d+)\.)?\s+([a-zA-Z /–—-]+?)(" + penalty_regexp + r")?\s*$", re.MULTILINE
    )
    for match in potential_header_lines.finditer(content):
        section = int(match.group(1))
        subsection = int(match.group(2)) if match.group(2) else None
        title = match.group(3).strip()
        penalty = match.group(4) or None

        if converter.is_actual_header(section, subsection, open_chunk.section, open_chunk.subsection):
            open_chunk.content = converter.get_chunk_content(chunk_start, match.start(), content)
            chunks.append(open_chunk)
            title = uncapitalize(title)
            open_chunk = IpgChunk(section=section, subsection=subsection, title=title, penalty=penalty, content=None)
            chunk_start = match.start()

    open_chunk.content = converter.get_chunk_content(chunk_start, len(content), content)
    chunks.append(open_chunk)
    return chunks


def extract(filepath: Path | str) -> tuple[datetime.date, [dict]] | None:
    converted = converter.parse_pdf(filepath)
    if not converted:
        return None
    effective_date, content = converted

    # We want to skipp the ToC that's between the Introduction and the rest of the document
    start_of_intro = re.compile(r"^INTRODUCTION\s*$", re.MULTILINE)
    end_of_intro = re.compile(r"^CONTENTS\s*$", re.MULTILINE)
    intro_content = cleanup.trim_content(content, start_of_intro, end_of_intro)

    start_of_main = re.compile(r"^1. [A-Z ]+$", re.MULTILINE)
    end_of_main = re.compile(r"^APPENDIX A — [\w\s]+$", re.MULTILINE)
    main_content = cleanup.trim_content(content, start_of_main, end_of_main)

    content = intro_content + main_content
    cleaner = cleanup.build([cleanup.remove_page_nums, cleanup.remove_url_endblocks])
    cleaned = cleaner(content)
    chunks = split_into_chunks(cleaned)

    for chunk in chunks:
        splitter = IpgParagraphSplitter(chunk.content)
        splitter.make_paragraphs()
        chunk.content = "\n\n".join(splitter.paragraphs)

    return effective_date, [c.model_dump() for c in chunks]
