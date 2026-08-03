#!/usr/bin/env python3
"""The kit's own tests. `python3 tests/test_appsite.py`, no pytest needed.

These cover the rules that are easy to break and hard to see: how deep a link
is written, which pages get a language switcher, and where a blank line goes.
The real gate is coarser and lives in the app — build the site, `git diff`,
expect nothing — but a failure here says *which* rule broke.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from appsite import Chrome, Page, Site
from appsite.blocks import cards, hero, landing, section
from appsite.legal import bullets, heading, muted, note, p, render

PAGES = (
    Page("home", "index.html"),
    Page("extra", "extra.html", translated=False, labels={c: "Extra" for c in
                                                          ["en", "de", "fr", "es", "it",
                                                           "pt", "ja", "ko", "el",
                                                           "uk", "ru"]}),
    Page("support", "support.html"),
    Page("privacy", "privacy.html"),
)
CHROME = Chrome(brand="App", icon="img/i.png", pages=PAGES, copyright="©")
SITE = Site(chrome=CHROME, out="site")

failures = []


def check(name, condition):
    print(f"  {'ok  ' if condition else 'FAIL'} {name}")
    if not condition:
        failures.append(name)


print("chrome")

header, _, _, root = CHROME.render("en", "index.html")
check("english home links itself as ./", '<a href="./" aria-current="page">' in header)
check("english assets are not prefixed", root == "")

header, _, _, root = CHROME.render("de", "index.html")
check("a translated home links itself, not the english root",
      '<a href="./" aria-current="page">' in header)
check("translated assets come from one level up", root == "../")
check("a translated page links a sibling flat", '<a href="support.html">' in header)
check("an untranslated page is reached one level up", '<a href="../extra.html">' in header)
check("the brand goes to this language's home", '<a class="brand" href="./">' in header)

_, _, alternates, _ = CHROME.render("de", "support.html")
check("alternates point at each language's copy of THIS page",
      '<link rel="alternate" hreflang="fr" href="../fr/support.html">' in alternates)
check("x-default is the english original",
      '<link rel="alternate" hreflang="x-default" href="../support.html">' in alternates)

_, footer, alternates, _ = CHROME.render("en", "extra.html")
check("a one-language page declares no alternates", alternates == "")
check("a one-language page gets no language switcher", "languages" not in footer)
check("its footer omits itself", "extra.html" not in footer)
check("its footer keeps the others", 'href="support.html"' in footer)

_, footer, _, _ = CHROME.render("ru", "privacy.html")
check("a translated page gets the switcher", 'class="languages"' in footer)
check("the current language is marked once", footer.count('aria-current="page"') == 1)

print("\ndocument")

markup = SITE.document("ja", "privacy.html", title="T", description="D", main="<main></main>")
check("the language is on <html>", '<html lang="ja">' in markup)
check("no blank line is left where alternates would be",
      "\n\n</head>" not in markup)
markup = SITE.document("en", "extra.html", title="T", description="D", main="<main></main>")
check("a one-language page still closes <head> cleanly",
      "\n\n</head>" not in markup and "</head>" in markup)

print("\nlegal blocks")

body = render([muted("d"), note("n"), heading("H"), p("a"), bullets(["x"]), p("b"),
               heading("H2"), p("c")])
check("a dateline is separated from what follows",
      '<p class="muted">d</p>\n\n  <div class="note">' in body)
check("a heading opens a gap", "</div>\n\n  <h3>H</h3>" in body)
check("prose under a heading stays with it", "<h3>H</h3>\n  <p>a</p>" in body)
check("a list stays with its paragraph", "<p>a</p>\n  <ul>" in body)
check("the next heading opens a gap", "</p>\n\n  <h3>H2</h3>" in body)
check("bullets are escaped", "<li>x</li>" in body)

print("\nlanding blocks")

page = landing(
    hero(headline="H", lead="L", eyebrow="E", buttons='  <div class="actions"></div>\n',
         parts=['  <div class="stats"></div>\n']),
    [section("One", ['  <p>x</p>\n']), section("Two", [cards([("a", "b")])])],
)
check("buttons sit against the lead", '</p>\n  <div class="actions">' in page)
check("a hero part is set off by a blank line",
      '</div>\n\n  <div class="stats">' in page)
check("sections are separated", "</section>\n\n<section>" in page)
check("the hero is outside the wrap", '</div>\n\n<div class="wrap">' in page)
check("headings are escaped, bodies are markup", "<h2>One</h2>" in page)

print()
if failures:
    print(f"{len(failures)} failed")
    sys.exit(1)
print("all tests passed")
