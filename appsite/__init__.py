"""appsite — one implementation of an App Store companion site.

A small app on the store needs the same five or six pages every time: what it
is, its songs or levels or decks, support, a privacy policy, terms, and — for
a German operator — an Impressum. In eleven languages that is 46 files, and
writing them twice is how the second app ends up with the first app's
navigation.

This package holds the structure. Each app holds its own words.

    from appsite import Chrome, Page, Site, blocks, legal, listing, check

See README.md for what belongs here and what does not.
"""

from .chrome import Chrome, Page
from .languages import LANGUAGES, Language
from .site import Site

__all__ = ["Chrome", "Page", "Site", "Language", "LANGUAGES"]
