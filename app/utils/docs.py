from dataclasses import asdict, dataclass

title = "Academy Ruins API"

description = """
This API provides information about Magic: the Gathering rules and policy documents. It was
primarily created to serve the [Academy Ruins](https://academyruins.com) project and the [Fryatog](
https://github.com/Fryyyyy/Fryatog/) rules bot, but it has found other uses since. You can find the source for the
project on [GitHub](https://github.com/lunakv/academyruins-api).

## Response Encoding and Formatting
All text responses returned by this API are guaranteed to be served in the form of UTF-8 encoded strings without a
BOM with LF (0x0A) line endings. *(Some very old CR text files may not yet be fully converted to this format)* Note
that the `/link` routes simply redirect to content hosted by other parties, and as such this API cannot make any
guarantees about their format.

The API preserves all typography extracted from the source files. This means using—among other things—“angled
quotation marks” and apostrophes, actual en and em dashes where appropriate, real ™ and ® symbols, etc. If you're
going to display data obtained by this API, make sure you’re able to handle characters outside of the standard ASCII
range. """


@dataclass
class Tag:
    name: str
    description: str | None = None


crTag = Tag("CR", "Resources pertaining to the parsed representation of the current Comprehensive Rules.")
mtrTag = Tag(
    "MTR",
    """
Resources pertaining to the parsed representation of the current version of the Magic: The Gathering Tournament Rules.

The parsed representation of the MTR consists of a flat list of sections. Those sections can be of three types:
- Non-numbered sections. These sections have a `title` and `content`, but don’t contain any values for `section` or
  `subsection`. The only such section currently present is the Introduction.
- Numbered section headers (e.g. “1. Tournament Fundamentals“). These have `title` and `section` values, but contain no
  `subsection` or `content`.
- Subsections (e.g. “1.1 Tournament Types“). The most common of the three. These contain values in all four fields.

Note that when section/subsection numbers are present, they aren’t part of the title. For example, the `title` field
for the aforementioned subsection would simply be `"Tournament Types"`.

The parsed MTR currently doesn’t include any appendices.
""",
)

redirectTag = Tag(
    "Redirects",
    """
Simple links to the most current versions of the documents (as hosted by WotC).

For ease of use, these links are also available under the domain [mtgdoc.link](https://mtgdoc.link). For example, both
<https://mtr.mtgdoc.link/> and <https://mtgdoc.link/mtr/> serve as aliases for the `/link/mtr` route.
""",
)

diffTag = Tag("Diffs")

filesTag = Tag("Files", "Historical versions of the raw documents themselves.")

tags: list[Tag] = [crTag, mtrTag, redirectTag, diffTag, filesTag]

tag_dicts: list[dict] = [asdict(tag) for tag in tags]
