#!/usr/bin/env python3
"""Generate impressum.html in every language.

The document and its framing notes live in `appsite.impressum`, shared with the
other apps because it identifies the same operator. This file only says which
site to write it into; the address itself is the `impressum` block in
site_config.py.

Nothing here is app-specific. Copy it and leave it alone.
"""

from site_config import SITE

from appsite import impressum

if __name__ == "__main__":
    print(f"wrote {impressum.write(SITE)} Impressum pages")
