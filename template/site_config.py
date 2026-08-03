"""Everything `appsite` needs to know about THIS APP.

The kit at Tools/appsite/ holds the structure — navigation, the document, the
page blocks, the checker. This file holds the facts that make those pages this
app's. Nothing else in Tools/appstore/ should describe the site's shape.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "appsite"))

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
    # dominant colour as --accent and leave the rest.
    palette={},                             # TODO(app)
)

#: What the App Store listing points at, so a renamed page fails the build
#: rather than App Review.
REQUIRED_PAGES = {"index.html", "privacy.html", "support.html", "terms.html",
                  "impressum.html"}
