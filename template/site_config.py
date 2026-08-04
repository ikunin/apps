"""Everything `appsite` needs to know about THIS APP.

The kit at vendor/appsite/ holds the structure — navigation, the document, the
page blocks, the checker. This file holds the facts that make those pages this
app's. Nothing else in this repository should describe the site's shape.
"""

import os
import sys


def _kit():
    """vendor/appsite, wherever in the tree this file happens to sit.

    Walking up beats a fixed number of `..` segments: this file belongs in
    appstore/ in every repository, but it keeps working from anywhere, and a
    missing submodule says so instead of failing as ModuleNotFoundError three
    imports later.
    """
    directory = os.path.dirname(os.path.abspath(__file__))
    while directory != os.path.dirname(directory):
        kit = os.path.join(directory, "vendor", "appsite")
        if os.path.isdir(os.path.join(kit, "appsite")):
            return kit
        directory = os.path.dirname(directory)
    raise SystemExit("vendor/appsite is missing — run: git submodule update --init")


sys.path.insert(0, _kit())

from appsite import Chrome, Page, Site  # noqa: E402

PAGES = (
    Page("home", "index.html"),
    Page("support", "support.html"),
    Page("privacy", "privacy.html"),
    Page("terms", "terms.html"),
    # German law wants the provider identification in German. It is the one
    # page here written by hand rather than generated.
    Page("impressum", "impressum.html", translated=False),
)

SITE = Site(
    chrome=Chrome(
        brand="App&nbsp;Name",              # TODO(app)
        icon="img/icon-512.png",
        pages=PAGES,
        copyright="© Igor Kunin 2026",
    ),
    out="site",
    metadata=os.path.join("fastlane", "metadata"),
    # Token overrides on the kit's stylesheet. Start with the app icon's
    # dominant colour as --accent and leave the rest. --accent is also the
    # colour this app's card takes on the portfolio at the root of the site.
    palette={},                             # TODO(app)
    # The App Store listing, once the app is live. The portfolio card shows a
    # button for it and leaves the button off while this is empty, so an
    # unreleased app needs no placeholder here.
    store="",                               # TODO(app)
)

#: What the App Store listing points at, so a renamed page fails the build
#: rather than App Review.
REQUIRED_PAGES = {"index.html", "privacy.html", "support.html", "terms.html",
                  "impressum.html"}
