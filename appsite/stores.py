"""Where the app can be had: one renderer for every way out to a store.

Two callers — a site's header and the app's card on the portfolio — and one
implementation, because the rules below are easy to get half right twice:

  · Every platform is its **store's own badge**, unretouched (badge.py):
    Apple's for an Apple platform, Microsoft's for Windows. This kit draws no
    button of its own for any store.
  · Several platforms are each **named** for the device, above their badge.
    Apple's artwork is identical on every Apple platform, so without the name
    three badges are three guesses.
  · A platform whose link is **empty** is not live. The header and the card
    write nothing for it — no dead link. A layout that exists to say where the
    app is coming (an app's own download section) can still show its badge
    with `way()`: unlinked, dimmed, and marked "coming soon".

`Site.store` — one URL, one App Store record — is the form every app started
with, and renders exactly the single unlabelled badge it always has.
"""

from . import badge
from .languages import LANGUAGES

#: Every platform this kit can name: its label, and the store whose badge it
#: wears. Labels are product names, which their owners ship untranslated in
#: every one of these languages — the same reason the badges' words are never
#: translated.
PLATFORMS = {
    "ios": ("iPhone &amp; iPad", badge.APPLE),
    "iphone": ("iPhone", badge.APPLE),
    "ipad": ("iPad", badge.APPLE),
    "mac": ("Mac", badge.APPLE),
    "tv": ("Apple&nbsp;TV", badge.APPLE),
    "watch": ("Apple&nbsp;Watch", badge.APPLE),
    "windows": ("Windows", badge.MICROSOFT),
}


def _entries(stores=(), store=""):
    """(platform, url) for every listed platform, live or not, in order.

    A lone `store` is one App Store record whose device nobody named, so its
    platform is "". An unknown platform is refused rather than guessed into
    somebody's badge.
    """
    found = []
    for platform, url in stores or ():
        if platform not in PLATFORMS:
            raise SystemExit(f"stores: unknown platform {platform!r} — "
                             f"one of {sorted(PLATFORMS)}")
        found.append((platform, url))
    if not found and store:
        found.append(("", store))
    return found


def store_of(platform):
    return PLATFORMS[platform][1] if platform else badge.APPLE


def live(stores=(), store=""):
    """(platform, url) for every platform with a link, in offered order."""
    return [(platform, url) for platform, url in _entries(stores, store) if url]


def families(stores=(), store=""):
    """The stores whose artwork a site needs: every listed platform's, live or
    not, since `way()` shows a coming platform's badge too. In first-listed
    order, each once."""
    found = []
    for platform, _ in _entries(stores, store):
        if store_of(platform) not in found:
            found.append(store_of(platform))
    return tuple(found)


def needs_badge(stores=(), store=""):
    """True when any platform is live, so a card or a header shows a badge."""
    return bool(live(stores, store))


def way(platform, url, *, language="en", root="", outward=None):
    """One platform's badge, unnamed — for a layout that already names it,
    such as an app's own per-platform card.

    With a url it is the link. Without one it is the same artwork, unlinked
    and dimmed, with "coming soon" in the page's language beneath it: a badge
    that looks clickable and goes nowhere is the dead link this kit refuses
    everywhere else.
    """
    store = store_of(platform)
    if url:
        outward = outward or (lambda target: target)
        return badge.link(outward(url), language, root, store)
    soon = LANGUAGES[language].nav["soon"]
    return (f'<span class="store-pending">'
            f'<span class="store-badge" aria-hidden="true">'
            f'{badge.image(language, root, store)}</span>'
            f'<span class="store-pending-label">{soon}</span></span>')


def links(stores=(), store="", *, language="en", root="", outward=None):
    """The markup for each live way out, one string per platform.

    `root` is how far this page sits from its own site (for the badge's image);
    `outward` rewrites a relative link for the page's depth and leaves a full
    URL alone — the header passes its own, a card needs none.
    """
    found = live(stores, store)
    out = []
    for platform, url in found:
        inner = way(platform, url, language=language, root=root, outward=outward)
        if len(found) > 1:
            inner = (f'<span class="store-for">'
                     f'<span class="store-for-label">{PLATFORMS[platform][0]}</span>'
                     f'{inner}</span>')
        out.append(inner)
    return out
