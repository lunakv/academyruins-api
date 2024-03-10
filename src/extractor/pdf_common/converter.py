"""
Utility functions for parsing the PDF into plain text
"""
import datetime
import os
import re
from tika import parser


def parse_pdf(filepath: str) -> tuple[str, datetime.date] | None:
    if os.getenv("USE_TIKA") != "1":
        return None

    args = [filepath]
    tika_server = os.getenv("TIKA_URL")

    if tika_server:
        args.append(tika_server)
    content = parse_from_file(*args)
    effective_date = get_effective_date(content)
    return content, effective_date


def parse_from_file(*args) -> str:
    return parser.from_file(*args)["content"]


def get_effective_date(content: str) -> datetime.date:
    effective_str = re.search(r"^Effective (.*)$", content, re.MULTILINE)
    return datetime.datetime.strptime(effective_str.group(1).strip(), "%B %d, %Y").date()


def is_actual_header(section: int, subsection: int, last_section: int, last_subsection: int | None) -> bool:
    # a simple test - header must follow immediately after the previous confirmed header
    # we could parse the ToC for more robust results, but this is sufficient for now
    return (
        (section == 1 and subsection is None and last_section is None)
        or (section == last_section + 1 and subsection is None)
        or (section == last_section and subsection == 1 and last_subsection is None)
        or (section == last_section and subsection == last_subsection + 1)
    )


def get_chunk_content(chunk_start: int, chunk_end: int, content: str) -> str:
    # content starts at the next line after the header
    start = content.find("\n", chunk_start)
    return content[start:chunk_end].strip()
