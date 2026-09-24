"""Apple's own "Download on the App Store" badge, one file per language.

The way into the store is artwork Apple licenses, not a button a site designs.
Their marketing guidelines are explicit about it: use only the badge artwork
they provide, never recreate it, never translate the words on it, and never
translate the mark *App Store* itself. A link styled to look like a way into
the store is exactly the thing they are asking nobody to draw, and this kit
drew one for a year.

So a page links the badge as an image, unretouched, and the rules that come
with it are in one place — here — rather than remembered at each call site:

  · **40 px** is Apple's minimum height onscreen, and so it is the height it
    is drawn at. Only the height is set; the width follows the artwork, which
    is how the proportions cannot drift.
  · **Clear space** of at least a quarter of that height on every side.
  · The **black** badge is the preferred one, and its grey border is part of
    the artwork rather than a frame this stylesheet may restyle.
  · **One badge per layout.**

The files are committed under `assets/badges/`, one per language the kit
builds in, and `refresh_badges.py` at the root of the kit is how they got
there. Committed rather than fetched while the site builds: a page that only
builds when Apple's CDN answers is a page that does not build on a train.

Guidelines: https://developer.apple.com/app-store/marketing/guidelines/
"""

import functools
import os
import shutil
from xml.etree import ElementTree

#: Apple's own locale for each language this kit builds in. Their badge
#: service names locales its own way — `it`, `ja`, `ko`, `el`, `uk` and `ru`
#: are `it-it`, `ja-jp`, `ko-kr`, `el-gr`, `uk-ua` and `ru-ru` there, and
#: Portuguese is Brazil's — so this cannot be derived from `Language.locale`,
#: which is what App Store Connect calls the same eleven. Read only when the
#: artwork is refreshed; a built site names the files by language.
LOCALES = {
    "en": "en-us", "de": "de-de", "fr": "fr-fr", "es": "es-es", "it": "it-it",
    "pt": "pt-br", "ja": "ja-jp", "ko": "ko-kr", "el": "el-gr", "uk": "uk-ua",
    "ru": "ru-ru",
}

#: Where the artwork comes from. Apple's marketing tools serve the same SVG
#: their download page hands out, addressable per language.
SOURCE = ("https://toolbox.marketingtools.apple.com/api/v2/badges"
          "/download-on-the-app-store/black/{locale}")

ARTWORK = os.path.join(os.path.dirname(__file__), "assets", "badges")

#: The directory the badges are copied into, inside a built site.
DIRECTORY = "badge"

#: The alt text, in English on every page, because the badge is Apple's
#: sentence about Apple's store and *App Store* is a mark that is never
#: translated. Writing our own eleven translations of it would be the same
#: mistake as drawing our own badge, one layer down; this is what Apple's
#: marketing tools emit alongside the localised artwork.
ALT = "Download on the App Store"

#: The height every badge is drawn at: Apple's minimum onscreen size, and the
#: one dimension the stylesheet sets. The width follows the artwork.
HEIGHT = 40


def file(language):
    """The badge for one language, as a built site holds it."""
    return f"{DIRECTORY}/app-store-{language}.svg"


@functools.lru_cache(maxsize=None)
def box(language):
    """(width, height) for this badge at `HEIGHT`, read from the artwork.

    The <img> carries it so the header reserves the right space before the SVG
    arrives instead of reflowing around it. Measured rather than written down:
    Apple's eleven exports are not one shape — Ukrainian's is 120.664 × 41
    where English's is 119.664 × 40 — and a number copied in here would be
    wrong for one language today and for another one after the next revision.
    """
    root = ElementTree.parse(os.path.join(ARTWORK, f"app-store-{language}.svg"))
    view = root.getroot().get("viewBox")
    if not view:
        raise SystemExit(f"app-store-{language}.svg: no viewBox to measure")
    _, _, width, height = (float(number) for number in view.replace(",", " ").split())
    return round(width * HEIGHT / height), HEIGHT


def link(href, language="en", root=""):
    """The way into the App Store, for any page in this kit.

    One implementation, two callers — a site's header and a card on the
    portfolio — because a badge drawn twice is a badge that is only fixed
    once. `root` is how far this page sits from the site it belongs to.
    """
    width, height = box(language)
    return (f'<a class="store-badge" href="{href}">'
            f'<img src="{root}{file(language)}" alt="{ALT}" '
            f'width="{width}" height="{height}" loading="lazy"></a>')


def copy(out, languages):
    """Put those languages' badges in `out/badge/`. Returns what it wrote."""
    written = []
    for language in languages:
        source = os.path.join(ARTWORK, f"app-store-{language}.svg")
        if not os.path.exists(source):
            raise SystemExit(
                f"{source}: no App Store badge for {language!r}. Apple has one "
                f"in fifty languages — add it to LOCALES and run refresh_badges.py")
        target = os.path.join(out, file(language))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copyfile(source, target)
        written.append(target)
    return written


def install(site):
    """The badges one app's site needs — none at all until it is on the store.

    An app with no listing links nowhere and carries no artwork, which is the
    same rule the header already follows for the link itself.
    """
    return copy(site.out, site.languages) if site.store else []
