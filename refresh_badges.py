#!/usr/bin/env python3
"""Download each store's official badge artwork into the kit.

    python3 refresh_badges.py

One SVG per store per language the kit builds in, straight from the store's own
badge service (Apple's marketing tools, Microsoft's badge page) and written to `appsite/assets/badges/` byte for byte. They are committed: the
guidelines say to use the artwork the store provides, and a site that fetched it
while building would stop building the day that service moved.

Run it when the kit learns a language, or if a store revises its badge. It
overwrites, prints what changed, and touches nothing else.
"""

import os
import sys
import urllib.request
from xml.etree import ElementTree

from appsite import badge


def main():
    os.makedirs(badge.ARTWORK, exist_ok=True)
    changed = total = 0
    for store in badge.STORES:
        for language, locale in store.locales.items():
            total += 1
            changed += fetch(store, language, locale)
    print(f"{changed} of {total} badges written to {badge.ARTWORK}")


def fetch(store, language, locale):
    """One badge. Returns 1 if the file changed, 0 if it did not."""
    url = store.source.format(locale=locale)
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            if response.status != 200:
                sys.exit(f"{url}: {response.status}")
            artwork = response.read()
    except OSError as problem:
        sys.exit(f"{url}: {problem}")
    # The exports are not one shape: some carry an XML: some carry an XML
    # declaration and an Illustrator comment ahead of the element. Ask the
    # parser what the root element is rather than what the bytes start with.
    try:
        root = ElementTree.fromstring(artwork)
    except ElementTree.ParseError as problem:
        sys.exit(f"{url}: not XML ({problem}) — has the service moved?")
    if not root.tag.endswith("svg"):
        sys.exit(f"{url}: root element is {root.tag}, not an SVG")
    target = os.path.join(badge.ARTWORK, f"{store.key}-{language}.svg")
    before = open(target, "rb").read() if os.path.exists(target) else b""
    if before == artwork:
        print(f"  {store.key} {language}  unchanged")
        return 0
    with open(target, "wb") as handle:
        handle.write(artwork)
    print(f"  {store.key} {language}  {'updated' if before else 'new'}, "
          f"{len(artwork)} bytes  ({locale})")
    return 1


if __name__ == "__main__":
    main()
