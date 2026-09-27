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

from dataclasses import dataclass


# eq=False: a store is itself, hashed by identity — `box()` caches per store,
# and the locale table would make a field-wise hash impossible anyway.
@dataclass(frozen=True, eq=False)
class Store:
    """One store's official badge: where its artwork comes from and how a page
    names it. The rules at the top of this module hold for every one of them —
    their artwork, unretouched, never a button we draw."""
    #: The file-name prefix in `assets/badges/` and in a built site's `badge/`.
    key: str
    #: The artwork's URL, per `locale`.
    source: str
    #: The store's own locale for each language this kit builds in.
    locales: dict
    #: The alt text, in English on every page: the badge is the store's own
    #: sentence, and its mark is never translated.
    alt: str
    #: The one thing we write when the badge fails to fetch.
    owner: str


#: Apple's own locale for each language this kit builds in. Their badge
#: service names locales its own way — `it`, `ja`, `ko`, `el`, `uk` and `ru`
#: are `it-it`, `ja-jp`, `ko-kr`, `el-gr`, `uk-ua` and `ru-ru` there, and
#: Portuguese is Brazil's — so this cannot be derived from `Language.locale`,
#: which is what App Store Connect calls the same eleven. Read only when the
#: artwork is refreshed; a built site names the files by language.
APPLE = Store(
    key="app-store",
    source=("https://toolbox.marketingtools.apple.com/api/v2/badges"
            "/download-on-the-app-store/black/{locale}"),
    locales={
        "en": "en-us", "de": "de-de", "fr": "fr-fr", "es": "es-es", "it": "it-it",
        "pt": "pt-br", "ja": "ja-jp", "ko": "ko-kr", "el": "el-gr", "uk": "uk-ua",
        "ru": "ru-ru",
    },
    alt="Download on the App Store",
    owner="Apple",
)

#: Microsoft's "Download from the Microsoft Store" badge, as their badge page
#: hands it out — the dark one, beside Apple's black.
#: Their locales are a third spelling: English and Portuguese carry a region
#: (`en-us`, `pt-br`) and the other nine are bare — `de-de` is a 404.
MICROSOFT = Store(
    key="microsoft",
    source="https://get.microsoft.com/images/{locale}%20dark.svg",
    locales={
        "en": "en-us", "de": "de", "fr": "fr", "es": "es", "it": "it",
        "pt": "pt-br", "ja": "ja", "ko": "ko", "el": "el", "uk": "uk", "ru": "ru",
    },
    alt="Download from the Microsoft Store",
    owner="Microsoft",
)

STORES = (APPLE, MICROSOFT)

# The names every caller used while Apple was the only store.
LOCALES = APPLE.locales
SOURCE = APPLE.source
ALT = APPLE.alt

ARTWORK = os.path.join(os.path.dirname(__file__), "assets", "badges")

#: The directory the badges are copied into, inside a built site.
DIRECTORY = "badge"

#: The height every badge is drawn at: Apple's minimum onscreen size, and the
#: one dimension the stylesheet sets. The width follows the artwork, so two
#: stores' badges side by side stand the same height without either stretched.
HEIGHT = 40


def file(language, store=APPLE):
    """The badge for one language, as a built site holds it."""
    return f"{DIRECTORY}/{store.key}-{language}.svg"


@functools.lru_cache(maxsize=None)
def box(language, store=APPLE):
    """(width, height) for this badge at `HEIGHT`, read from the artwork.

    The <img> carries it so the header reserves the right space before the SVG
    arrives instead of reflowing around it. Measured rather than written down:
    Apple's eleven exports are not one shape — Ukrainian's is 120.664 × 41
    where English's is 119.664 × 40 — and a number copied in here would be
    wrong for one language today and for another one after the next revision.
    """
    name = f"{store.key}-{language}.svg"
    root = ElementTree.parse(os.path.join(ARTWORK, name))
    view = root.getroot().get("viewBox")
    if not view:
        raise SystemExit(f"{name}: no viewBox to measure")
    _, _, width, height = (float(number) for number in view.replace(",", " ").split())
    return round(width * HEIGHT / height), HEIGHT


def image(language="en", root="", store=APPLE):
    """The badge artwork itself, as an <img> — linked or not is the caller's."""
    width, height = box(language, store)
    return (f'<img src="{root}{file(language, store)}" alt="{store.alt}" '
            f'width="{width}" height="{height}" loading="lazy">')


def link(href, language="en", root="", store=APPLE):
    """The way into a store, for any page in this kit.

    One implementation, two callers — a site's header and a card on the
    portfolio — because a badge drawn twice is a badge that is only fixed
    once. `root` is how far this page sits from the site it belongs to.
    """
    return f'<a class="store-badge" href="{href}">{image(language, root, store)}</a>'


def copy(out, languages, stores=(APPLE,)):
    """Put those languages' badges, for those stores, in `out/badge/`.
    Returns what it wrote."""
    written = []
    for store in stores:
        for language in languages:
            source = os.path.join(ARTWORK, f"{store.key}-{language}.svg")
            if not os.path.exists(source):
                raise SystemExit(
                    f"{source}: no {store.owner} badge for {language!r} — add it "
                    f"to that store's locales and run refresh_badges.py")
            target = os.path.join(out, file(language, store))
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copyfile(source, target)
            written.append(target)
    return written


def install(site):
    """The badges one app's site needs — none at all until it names a store.

    Artwork for every store a listed platform belongs to, live or not: a
    platform whose listing is not open yet still shows its badge on the app's
    own page, unlinked, marked as coming (stores.way). An app with no store at
    all carries none.
    """
    from . import stores
    return copy(site.out, site.languages, stores.families(site.stores, site.store))
