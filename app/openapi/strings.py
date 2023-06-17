from dataclasses import asdict, dataclass

title = "Academy Ruins API"

description = """This API provides information about Magic: the Gathering rules and policy documents. Created
primarily as a backend for the [Academy Ruins](https://academyruins.com) project, it now serves various apps and
services in need of automated access to these resources. It is currently still in its prerelease stage of
development, so some breaking changes may occur with each release and backwards compatibility isn't necessarily
guaranteed until the 1.0 release is reached. (Though significant breaking changes should be very rare.)"""

license_info = {"name": "AGPL v3.0", "url": "https://www.gnu.org/licenses/agpl-3.0.txt"}

contact_info = {"name": "Project repository", "url": "https://github.com/lunakv/academyruins-api"}


@dataclass
class Tag:
    name: str
    description: str | None = None


formattingTag = Tag(
    "Response Encoding and Formatting",
    """
All text responses returned by this API are guaranteed to be served in the form of UTF-8 encoded strings without a
BOM with LF (0x0A) line endings. *(Some very old CR text files may not yet be fully converted to this format)* Note
that the `/link` routes simply redirect to content hosted by other parties, and as such this API cannot make any
guarantees about their format.

The API preserves all typography extracted from the source files. This means using—among other things—“angled
quotation marks” and apostrophes, actual en and em dashes where appropriate, real ™ and ® symbols, etc. If you're
going to display data obtained by this API, make sure you’re able to handle characters outside of the standard ASCII
range.""",
)

limitingTag = Tag(
    "Rate Limiting",
    """
The API runs on hardware with relatively few resources. To help ensure its availability, any client using the API is
limited to the maximum rate of 10 requests per second. It is therefore recommended that clients try to ensure at
least a 100 ms delay between requests. Sending requests at a greater rate for a sustained period of time may result
in an error response with the status code 429 and body `{"detail": "Too many requests."}`. In such situations it is
recommended to wait at least two seconds before resuming calls to the API.

The data served by this project does not tend to change very often, so unless immediacy is of utmost importance,
we encourage you to cache any served data for a period of at least 24 hours.

Due to its large current computational complexity, the `/cr/trace` endpoint has a separate limit of 1 request per
second. These limits are subject to change in future versions of the API.""",
)


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

general_tags = [formattingTag, limitingTag]

route_tags: list[Tag] = [crTag, mtrTag, redirectTag, diffTag, filesTag]

tag_dicts: list[dict] = [asdict(tag) for tag in [*general_tags, *route_tags]]

tag_groups = {
    "General": general_tags,
    "Routes": route_tags,
}
