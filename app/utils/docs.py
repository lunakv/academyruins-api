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