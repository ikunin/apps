"""Check a built site holds together, before anyone publishes it.

The App Store listing links to a privacy page and a support page, and App
Review follows the privacy link. A page that 404s there is a rejection, so
this belongs in the app's `make check` and again in its Pages workflow.

Only local links are followed. Checking that an external site is up would make
the build depend on somebody else's uptime, which is a worse failure than the
one it would catch.
"""

import os
import re
import sys
from html.parser import HTMLParser

from . import portfolio


class Links(HTMLParser):
    """Every href and src on a page, with the line it came from."""

    def __init__(self):
        super().__init__()
        self.found = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ("href", "src") and value:
                self.found.append((value, self.getpos()[0]))


def local_target(value):
    """The file a link points at, or None if it leaves the site."""
    # `tel:` belongs here with `mailto:` — an Impressum carries a telephone
    # link, and without this the checker looked for a file named after the
    # whole `tel:` URI.
    if value.startswith(("http://", "https://", "mailto:", "tel:", "#", "//",
                         "data:")):
        return None
    return value.split("#", 1)[0].split("?", 1)[0] or None


def images_without_alt(markup):
    """Every <img> on a page that a screen reader would have nothing to say
    about. One definition, so the portfolio at the root of the Pages site is
    held to the same rule as the app pages."""
    return [img for img in re.findall(r"<img\b[^>]*>", markup)
            if 'alt="' not in img]


#: Every app in the family, by its printed name. Extend when one joins.
#:
#: A built page must never carry a name that is not this app's own. The kit
#: seeds a new site with a shipped app's words on purpose — § 4 of the recipe is
#: rewriting them — and what survives that rewrite is another app's promise on
#: this app's legal page, in eleven languages, linked from an App Store listing.
#: It reached the open web once as a page title, because the recipe sends you to
#: the text tables and the name was in the plumbing.
FAMILY = ["TappyMusic", "Harbor Rush", "SpeedyCards", "VideoSqueezer", "MorseHero"]


def other_apps_named(markup, own):
    """Names in `markup` that belong to a different app in the family.

    Case-sensitive on purpose: a slug in a URL — `apps/tappymusic/` on that
    app's own pages, `../../` on everyone else's — is a path, not a claim.
    """
    return [name for name in FAMILY if name != own and name in markup]


def check_pages(site, *, required, impressum):
    problems = []
    out = site.out
    own = portfolio.plain(site.impressum.get("app") or site.chrome.brand)

    # Every page, at the root and in each language directory. Walking rather
    # than naming them is the point: a translated page nobody remembered to
    # list here would be the one with the broken link.
    pages = sorted(
        os.path.relpath(os.path.join(base, name), out)
        for base, _, names in os.walk(out)
        for name in names
        if name.endswith(".html")
    )

    for missing in sorted(set(required) - set(pages)):
        problems.append(f"{out}/{missing}: missing, and the listing links to it")

    for page in pages:
        with open(os.path.join(out, page), encoding="utf-8") as handle:
            markup = handle.read()

        parser = Links()
        parser.feed(markup)
        for value, line in parser.found:
            target = local_target(value)
            if target is None:
                continue
            base = os.path.join(out, os.path.dirname(page))
            if not os.path.exists(os.path.normpath(os.path.join(base, target))):
                problems.append(f"{out}/{page}:{line}: {value} does not exist")

        # An image with no alt text is unreadable to a screen reader.
        for _ in images_without_alt(markup):
            problems.append(f"{out}/{page}: an <img> has no alt text")

        if "<title>" not in markup:
            problems.append(f"{out}/{page}: no <title>")

        for name in other_apps_named(markup, own):
            problems.append(f"{out}/{page}: says {name}, which is a different app")

        # German law requires the provider identification to be reachable from
        # every page — "leicht erkennbar, unmittelbar erreichbar und ständig
        # verfügbar" — so a page that does not link it is not compliant. Any
        # depth: translated pages link "../impressum.html".
        if impressum and impressum not in markup \
                and os.path.basename(page) != impressum:
            problems.append(f"{out}/{page}: does not link the Impressum")

    # An Impressum missing the address or telephone number is worse than none:
    # § 5 DDG requires both, and an incomplete one is what gets abgemahnt.
    if impressum:
        path = os.path.join(out, impressum)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as handle:
                if "IMPRESSUM-PLATZHALTER" in handle.read():
                    problems.append(
                        f"{out}/{impressum}: still has placeholders — § 5 DDG "
                        "needs a real postal address and telephone number"
                    )

    return problems, len(pages)


def check_listing_urls(site):
    """The URLs in the App Store metadata resolve to pages that are on disk."""
    problems = []
    if not os.path.isdir(site.metadata):
        return [f"{site.metadata}: missing"]

    def read(locale, field):
        path = os.path.join(site.metadata, locale, field)
        if not os.path.exists(path):
            return None
        with open(path, encoding="utf-8") as handle:
            return handle.read().strip()

    # Every listing URL points at one page in this repository, so the check
    # that matters is the same for all of them: resolve the URL to a file and
    # see whether it is there. The English marketing URL is the site root, and
    # everything else hangs off it.
    root = read("en-US", "marketing_url.txt")
    if not root:
        return [f"{site.metadata}/en-US/marketing_url.txt: missing"]
    if not root.endswith("/"):
        root += "/"

    expected = {"support_url.txt": "support.html",
                "privacy_url.txt": "privacy.html"}
    for locale in sorted(os.listdir(site.metadata)):
        if not os.path.isdir(os.path.join(site.metadata, locale)):
            continue
        for field in ["support_url.txt", "privacy_url.txt", "marketing_url.txt"]:
            url = read(locale, field)
            if url is None:
                continue
            if not url.startswith("https://"):
                problems.append(
                    f"{locale}/{field}: not https — App Review requires it")
            if not url.startswith(root):
                problems.append(f"{locale}/{field}: {url} is not on {root}")
                continue

            target = url[len(root):] or "index.html"
            if target.endswith("/"):
                target += "index.html"
            if not os.path.exists(os.path.join(site.out, target)):
                problems.append(
                    f"{locale}/{field}: {url} has no page at {site.out}/{target}")
            # A renamed page must not leave the listing pointing at the wrong
            # kind of page — a privacy URL that resolves to the terms would
            # pass the existence check and fail review.
            page = expected.get(field)
            if page and os.path.basename(target) != page:
                problems.append(f"{locale}/{field}: does not end in {page}")

    return problems


#: What App Store Connect will accept, in characters. It REJECTS rather than
#: truncates, and it does so at upload — so a subtitle one character over costs
#: a round trip through a build that has already been made. Counted in Python
#: characters, which is what Connect counts too: a Japanese subtitle of eleven
#: characters is eleven, not its length in bytes.
#:
#: Sources: App Store Connect's own field limits. `name` is 30 and `subtitle`
#: is 30; the pair is the most common overrun, and the one that has happened.
LISTING_LIMITS = {
    "name": 30,
    "subtitle": 30,
    "keywords": 100,
    "promotional_text": 170,
    "description": 4000,
    "release_notes": 4000,
}


def check_listing_limits(site, limits=None):
    """Listing fields are within what App Store Connect accepts.

    Every locale, not just the development one: a translation is longer than
    its English source more often than not, and the one that overran here was
    French at 31 characters against a limit of 30.
    """
    limits = LISTING_LIMITS if limits is None else limits
    problems = []
    if not os.path.isdir(site.metadata):
        return [f"{site.metadata}: missing"]

    for locale in sorted(os.listdir(site.metadata)):
        directory = os.path.join(site.metadata, locale)
        if not os.path.isdir(directory) or locale == "review_information":
            continue
        for field, limit in sorted(limits.items()):
            path = os.path.join(directory, f"{field}.txt")
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8") as handle:
                length = len(handle.read().strip())
            if length > limit:
                problems.append(
                    f"{locale}/{field}.txt: {length} characters, "
                    f"App Store Connect allows {limit}"
                )
    return problems


def main(site, *, required, impressum="impressum.html"):
    """Run every check and exit non-zero on any problem."""
    print("Website")
    problems, pages = check_pages(site, required=required, impressum=impressum)
    listing = check_listing_urls(site) + check_listing_limits(site)

    for problem in problems + listing:
        print(f"  FAIL {problem}")
    if problems or listing:
        print(f"\n{len(problems) + len(listing)} problems")
        sys.exit(1)

    print(f"  ok   {pages} pages, every internal link resolves")
    print("  ok   every image has alt text")
    print("  ok   no page names another app in the family")
    print("  ok   the listing URLs point into this site, in every locale")
    print("  ok   every listing field is within App Store Connect's limits")
    print("\nall tests passed")
