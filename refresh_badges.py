#!/usr/bin/env python3
"""Download Apple's App Store badge artwork into the kit.

    python3 refresh_badges.py

One SVG per language the kit builds in, straight from Apple's marketing tools
and written to `appsite/assets/badges/` byte for byte. They are committed: the
guidelines say to use the artwork Apple provides, and a site that fetched it
while building would stop building the day that service moved.

Run it when the kit learns a language, or if Apple revises the badge. It
overwrites, prints what changed, and touches nothing else.
"""

import os
import sys
import urllib.request
from xml.etree import ElementTree

from appsite import badge


def main():
    os.makedirs(badge.ARTWORK, exist_ok=True)
    changed = 0
    for language, locale in badge.LOCALES.items():
        url = badge.SOURCE.format(locale=locale)
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                if response.status != 200:
                    sys.exit(f"{url}: {response.status}")
                artwork = response.read()
        except OSError as problem:
            sys.exit(f"{url}: {problem}")
        # Apple's eleven exports are not one file: some carry an XML
        # declaration and an Illustrator comment ahead of the element. Ask the
        # parser what the root element is rather than what the bytes start with.
        try:
            root = ElementTree.fromstring(artwork)
        except ElementTree.ParseError as problem:
            sys.exit(f"{url}: not XML ({problem}) — has the service moved?")
        if not root.tag.endswith("svg"):
            sys.exit(f"{url}: root element is {root.tag}, not an SVG")
        target = os.path.join(badge.ARTWORK, f"app-store-{language}.svg")
        before = open(target, "rb").read() if os.path.exists(target) else b""
        if before == artwork:
            print(f"  {language}  unchanged")
            continue
        with open(target, "wb") as handle:
            handle.write(artwork)
        print(f"  {language}  {'updated' if before else 'new'}, "
              f"{len(artwork)} bytes  ({locale})")
        changed += 1
    print(f"{changed} of {len(badge.LOCALES)} badges written to {badge.ARTWORK}")


if __name__ == "__main__":
    main()
