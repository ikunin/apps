#!/usr/bin/env python3
"""Check an app's text tables for the mistakes translation review misses.

Run from an app's repository, pointing at the directory holding its
site_text_*.py and make_site_translations.py:

    python3 vendor/appsite/check_text.py --texts appstore

Two checks, both from real failures:

**Out-of-script characters.** A Cyrillic word inside a Japanese sentence, or a
Chinese character inside a Russian one, reads as fine to anyone who does not
read that language — and neither the site build nor a native reviewer of some
*other* language will catch it. This has happened twice in these tables.

**Another app's vocabulary.** Renaming "TappyMusic" to "SpeedyCards" across a
file renames the app but not what the app is *about*, so a card game's support
page kept asking about "a particular song". The check looks for words that
belong to a different app in this family.

Neither check can prove a translation is good. They catch the class of error
that survives a careful read, which is the class worth automating.
"""

import argparse
import ast
import os
import re
import sys

#: Scripts a language should never contain. Latin is omitted deliberately —
#: brand names, `speedycards://`, "Game Center" and "iCloud" are Latin in every
#: language here, and flagging them would make the check useless.
FOREIGN = {
    "cyrillic": r"[Ѐ-ӿ]",
    "kana": r"[぀-ヿ]",
    "han": r"[一-鿿]",
    "hangul": r"[가-힯]",
    "greek": r"[Ͱ-Ͽ]",
}
#: Which of those each language legitimately uses. Japanese uses han and kana;
#: Korean uses hangul and, rarely, han.
NATIVE = {
    "en": (), "de": (), "fr": (), "es": (), "it": (), "pt": (),
    "ja": ("kana", "han"), "ko": ("hangul", "han"),
    "el": ("greek",), "uk": ("cyrillic",), "ru": ("cyrillic",),
}

#: Words that mean one app and would be nonsense in another. Extend when an
#: app joins the family.
OTHER_APPS = {
    "tappymusic": ["melody", "melodies", "clipart", "soundfont", "nursery"],
    "harborrush": ["harbor", "harbour", "iceberg", "berth"],
    "speedycards": ["shuffle", "solitaire", "deck of cards"],
}


def tables(directory):
    """Every string in every *.py in `directory`, as (file, language, key, text)."""
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".py") or name.startswith("check"):
            continue
        path = os.path.join(directory, name)
        try:
            tree = ast.parse(open(path, encoding="utf-8").read(), filename=path)
        except SyntaxError as error:
            yield path, None, None, f"__syntax__:{error.lineno}: {error.msg}"
            continue
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            try:
                value = ast.literal_eval(node.value)
            except ValueError:
                continue          # f-strings and names; not a literal table
            if not isinstance(value, dict):
                continue
            for language, entry in value.items():
                if language not in NATIVE or not isinstance(entry, dict):
                    continue
                for key, item in entry.items():
                    for text in flatten(item):
                        yield path, language, key, text


def flatten(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from flatten(item)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--texts", required=True, help="directory of text tables")
    parser.add_argument("--app", help="this app's key in OTHER_APPS, to skip its own words")
    args = parser.parse_args()

    problems, checked = [], 0
    for path, language, key, text in tables(args.texts):
        if language is None:
            problems.append(f"{path}: {text}")
            continue
        checked += 1
        for script, pattern in FOREIGN.items():
            if script in NATIVE[language]:
                continue
            hit = re.search(pattern, text)
            if hit:
                problems.append(
                    f"{os.path.basename(path)} {language}/{key}: {script} "
                    f"{hit.group()!r} in {text[:60]!r}")
        for app, words in OTHER_APPS.items():
            if app == args.app:
                continue
            for word in words:
                if re.search(rf"\b{word}\b", text, re.I):
                    problems.append(
                        f"{os.path.basename(path)} {language}/{key}: "
                        f"{app} word {word!r} in {text[:60]!r}")

    print("Text")
    for problem in problems:
        print(f"  FAIL {problem}")
    if problems:
        print(f"\n{len(problems)} problems")
        sys.exit(1)
    print(f"  ok   {checked} strings, none in the wrong script")
    print("  ok   no other app's vocabulary")
    print("\nall tests passed")


if __name__ == "__main__":
    main()
