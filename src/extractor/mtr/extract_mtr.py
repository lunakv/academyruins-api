import datetime
import os
import re
from pathlib import Path

from tika import parser

from src.mtr.schemas import MtrChunk
from src.extractor.pdf_common.paragraph_splitter import ParagraphSplitter
from src.extractor.pdf_common import cleanup, converter


def split_into_chunks(content: str) -> [MtrChunk]:
    """Separates the parsed MTR into a list of sections and subsections"""
    chunks = []
    open_chunk = MtrChunk(section=None, subsection=None, title="Introduction", content=None)
    chunk_start = 0

    potential_header_lines = re.compile(r"^(\d+)\.(\d+)? +([a-zA-Z /-]+)$", re.MULTILINE)
    for match in potential_header_lines.finditer(content):
        section = int(match.group(1))
        subsection = int(match.group(2)) if match.group(2) else None
        title = match.group(3).strip()

        if converter.is_actual_header(section, subsection, open_chunk.section, open_chunk.subsection):
            open_chunk.content = converter.get_chunk_content(chunk_start, match.start(), content)
            chunks.append(open_chunk)
            open_chunk = MtrChunk(section=section, subsection=subsection, title=title, content=None)
            chunk_start = match.start()

    open_chunk.content = converter.get_chunk_content(chunk_start, len(content), content)
    chunks.append(open_chunk)
    return chunks


def extract(filepath: Path | str) -> (datetime.date, [dict]):
    converted = converter.parse_pdf(filepath)
    if not converted:
        return None
    content, effective_date = converted

    start_of_content = re.compile(r"^Introduction\s*$", re.MULTILINE)
    end_of_content = re.compile(r"^Appendix [A-Z]—[a-zA-Z ]*$", re.MULTILINE)
    cleaner = cleanup.build([cleanup.remove_page_nums, cleanup.remove_url_endblocks])
    content = cleaner(cleanup.trim_content(content, start_of_content, end_of_content))
    chunks = split_into_chunks(content)

    for chunk in chunks:
        # headers of each numbered section (X.0) don't have any content and don't need to be cleaned
        if chunk.section is not None and chunk.subsection is None:
            chunk.content = None
        else:
            splitter = ParagraphSplitter(chunk.content)
            splitter.make_paragraphs()
            chunk.content = "\n\n".join(splitter.paragraphs)

    return effective_date, [c.model_dump() for c in chunks]
