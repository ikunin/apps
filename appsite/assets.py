"""Put the kit's own files where the pages expect them.

The stylesheet is structure, not content: it draws the blocks in blocks.py, so
a change to one is usually a change to both. Two copies would drift the first
time somebody restyled a card in one app.

An app that wants different colours overrides the tokens rather than forking
the file — `Site.palette` becomes a `:root` block appended to the end, which is
enough for an accent, a background and a set of highlight hues.

The App Store badge rides along here rather than in each app's build script:
the kit gained it in one commit and every app that rebuilds gets it, where
eleven copies of a two-line install step would have been eleven chances to
have one app still drawing its own button.
"""

import os
import re
import shutil

from . import badge

STYLESHEET = os.path.join(os.path.dirname(__file__), "assets", "style.css")


def default_token(name):
    """What one custom property is before any app overrides it.

    Read out of the stylesheet rather than written down a second time here: an
    app that sets no palette still renders in a colour, and the portfolio card
    has to be able to say which one. The first definition wins, which is the
    dark one — the light block below it is a media query.
    """
    with open(STYLESHEET, encoding="utf-8") as handle:
        found = re.search(rf"--{name}:\s*([^;]+);", handle.read())
    return found.group(1).strip() if found else ""


def install(site):
    """Write the kit's assets into the site directory.

    The stylesheet, whose path it returns, and — for an app that is on the
    store — Apple's badge in each language this site is built in.
    """
    os.makedirs(site.out, exist_ok=True)
    badge.install(site)
    target = os.path.join(site.out, site.stylesheet)
    if not site.palette:
        shutil.copyfile(STYLESHEET, target)
        return target

    with open(STYLESHEET, encoding="utf-8") as handle:
        css = handle.read()
    overrides = "".join(f"  --{name}: {value};\n"
                        for name, value in site.palette.items())
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(css)
        handle.write(f"\n/* {site.chrome.brand} */\n:root {{\n{overrides}}}\n")
    return target
