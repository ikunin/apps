"""Where the app can be had: one renderer for every way out to a store.

Two callers — a site's header and the app's card on the portfolio — and one
implementation, because the rules below are easy to get half right twice:

  · An **Apple** platform is Apple's badge, unretouched (see badge.py).
  · Any **other** platform — Windows, sold directly — is a plain link this kit
    does draw, with a translated verb on it. It never borrows the App Store
    badge: that artwork is Apple's sentence about Apple's store.
  · Several platforms are each **named** for the device, above their link. The
    badge artwork is identical on every Apple platform, so without the name
    three badges are three guesses; a non-Apple link is always named, because
    "Download" on its own does not say for what.
  · A platform whose link is **empty** writes nothing — an unreleased record
    carries no dead link.

`Site.store` — one URL, one App Store record — is the form every app started
with, and renders exactly the single unlabelled badge it always has.
"""

import html

from . import badge
from .languages import LANGUAGES

#: Apple's product names, which Apple ships untranslated in every one of these
#: languages — the same reason the badge's own words are never translated.
APPLE = {
    "ios": "iPhone &amp; iPad",
    "iphone": "iPhone",
    "ipad": "iPad",
    "mac": "Mac",
    "tv": "Apple&nbsp;TV",
    "watch": "Apple&nbsp;Watch",
}

#: Platforms sold outside the App Store. The name is a product name, so it is
#: not translated either; the verb on the link is (`Language.nav`).
DIRECT = {
    "windows": "Windows",
}

#: What a direct link invites you to do. Each is a key in `Language.nav`.
ACTIONS = ("download", "buy")


def live(stores=(), store=""):
    """(platform, url, action) for every platform with a link, in offered order.

    An entry is (platform, url) or (platform, url, action); action defaults to
    "download" and only means anything for a direct link. A lone `store` is one
    App Store record whose device nobody named, so its platform is "".
    """
    found = []
    for entry in stores or ():
        platform, url, *rest = entry
        action = rest[0] if rest else "download"
        if platform not in APPLE and platform not in DIRECT:
            raise SystemExit(f"stores: unknown platform {platform!r} — "
                             f"one of {sorted(APPLE) + sorted(DIRECT)}")
        if action not in ACTIONS:
            raise SystemExit(f"stores: {platform}: action {action!r} is not one of {ACTIONS}")
        if url:
            found.append((platform, url, action))
    if not found and store:
        found.append(("", store, "download"))
    return found


def needs_badge(stores=(), store=""):
    """True when any live platform is Apple's, so the artwork must be installed."""
    return any(platform not in DIRECT for platform, _, _ in live(stores, store))


def links(stores=(), store="", *, language="en", root="", outward=None):
    """The markup for each way out, one string per platform.

    `root` is how far this page sits from its own site (for the badge's image);
    `outward` rewrites a relative link for the page's depth and leaves a full
    URL alone — the header passes its own, a card needs none.
    """
    outward = outward or (lambda url: url)
    found = live(stores, store)
    named = len(found) > 1
    out = []
    for platform, url, action in found:
        if platform in DIRECT:
            label = html.escape(LANGUAGES[language].nav[action])
            inner = f'<a class="store-direct" href="{outward(url)}">{label}</a>'
        else:
            inner = badge.link(outward(url), language, root)
        if named or platform in DIRECT:
            name = APPLE.get(platform) or DIRECT[platform]
            inner = (f'<span class="store-for">'
                     f'<span class="store-for-label">{name}</span>{inner}</span>')
        out.append(inner)
    return out
