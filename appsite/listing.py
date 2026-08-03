"""Read the App Store listing, so the site and the store cannot disagree.

The landing page's headline and opening paragraph come from the listing rather
than from the site's own copy. Those words are already translated, already
reviewed, and are what a customer meets before they ever reach the site. A
second translation of the same pitch is a second thing to keep in step, and it
would drift.

Layout is fastlane's `metadata/<locale>/<field>.txt`, which is also what App
Store Connect's own upload tools expect.
"""

import os
import re

from .languages import LANGUAGES


def read(site, language, field):
    locale = LANGUAGES[language].locale
    path = os.path.join(site.metadata, locale, f"{field}.txt")
    with open(path, encoding="utf-8") as handle:
        return handle.read().strip()


def lead(site, language):
    """The first paragraph of the description — the app in one breath."""
    return read(site, language, "description").split("\n\n")[0]


def headline(site, language):
    """The subtitle, split into a plain half and a half worth lighting up.

    Usually two sentences, and the second carries the promise, so it takes the
    colour. Three splits, in order: a full stop and a space; a Japanese 。,
    which is never followed by a space; a comma, for Korean subtitles that
    carry no sentence punctuation at all. If none fires, the whole line glows
    rather than leaving an empty span.
    """
    subtitle = read(site, language, "subtitle")
    parts = re.split(r"(?<=[.!?])\s+", subtitle, maxsplit=1)
    if len(parts) == 1:
        # Japanese and Chinese do not put a space after 。, so the rule above
        # never fires and the whole subtitle ended up in the glowing half.
        parts = re.split(r"(?<=[。！？])(?=.)", subtitle, maxsplit=1)
    if len(parts) == 1:
        comma = re.split(r"(?<=[、，,])\s*", subtitle, maxsplit=1)
        parts = comma if len(comma) > 1 and comma[1] else ["", subtitle]
    return parts[0], parts[1] if len(parts) > 1 else ""
