#!/usr/bin/env python3
"""The kit's own tests. `python3 tests/test_appsite.py`, no pytest needed.

These cover the rules that are easy to break and hard to see: how deep a link
is written, which pages get a language switcher, and where a blank line goes.
The real gate is coarser and lives in the app — build the site, `git diff`,
expect nothing — but a failure here says *which* rule broke.
"""

import ast
import json
import os
import pathlib
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from appsite import Chrome, Page, Site, assets, impressum, portfolio
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


def raises(function, *arguments):
    """True when a build refuses to go on. The kit says no with SystemExit."""
    try:
        function(*arguments)
    except SystemExit:
        return True
    return False


#: The oldest Python an app's CI runs. Nothing here may need newer syntax:
#: this package is imported by three repositories and cannot pick their
#: interpreter.
OLDEST = (3, 11)

print(f"syntax, as Python {OLDEST[0]}.{OLDEST[1]}")

KIT = pathlib.Path(__file__).resolve().parent.parent
for source in sorted(KIT.rglob("*.py")):
    if ".git" in source.parts:
        continue
    try:
        ast.parse(source.read_text(), filename=str(source), feature_version=OLDEST)
        ok, detail = True, ""
    except SyntaxError as error:
        ok, detail = False, f" — line {error.lineno}: {error.msg}"
    check(f"{source.relative_to(KIT)} parses{detail}", ok)

print("\nchrome")

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
check("a hero with nothing to add under the headline gets no empty lead",
      'class="lead"' not in hero(headline="H", lead=""))

print("\nthe impressum's app-specific block")

# The § 5 identification is shared with the portfolio at the root of the Pages
# site, which is not an app. What follows is the wording as it stands on 33
# published pages: if this test fails, those pages moved, and the only right
# reason for that is that somebody meant it.
IMPRESSUM_PAGES = (
    Page("home", "index.html"),
    Page("privacy", "privacy.html"),
    Page("terms", "terms.html"),
    Page("impressum", "impressum.html"),
)
IMPRESSUM_SITE = Site(
    chrome=Chrome(brand="App", icon="img/i.png", pages=IMPRESSUM_PAGES, copyright="©"),
    out="site",
    impressum={"app": "App", "name": "N", "street": "S", "postcode": "1",
               "city": "C", "country": "D", "phone": "+49 30 1",
               "email": "a@b.example"},
)
STANDING = """  <h3>Verkauf über den App&nbsp;Store</h3>
  <p>
    Die App und alle In-App-Käufe werden über den Apple App&nbsp;Store
    vertrieben. Vertragspartner für den Kauf ist Apple; Rückerstattungen
    laufen über
    <a href="https://reportaproblem.apple.com">reportaproblem.apple.com</a>.
  </p>

  <h3>Datenschutz</h3>
  <p>
    Verantwortlicher im Sinne der DSGVO ist der oben genannte Diensteanbieter.
    Einzelheiten in der
    <a href="privacy.html">Datenschutzerklärung</a>,
    siehe auch die
    <a href="terms.html">Nutzungsbedingungen</a>.
  </p>
"""
standard = impressum.page(IMPRESSUM_SITE, "de")
check("an app's impressum is unchanged by the seam the portfolio uses",
      STANDING in standard)
check("and it still carries its own language's note", "Impressum" in standard)

replaced = impressum.page(IMPRESSUM_SITE, "de", about="  <p>ABOUT</p>\n",
                          note="NOTE")
check("a caller can replace the paragraphs that are about an app",
      "<p>ABOUT</p>" in replaced and "reportaproblem" not in replaced)
check("its own note is used as given, not formatted again",
      "<p>NOTE</p>" in replaced)
check("what is about the operator stays either way",
      "Angaben gemäß § 5 DDG" in replaced and "Haftung für Links" in replaced)

print("\nportfolio")

CONFIG = portfolio.load_config()


def app_site(directory, *, subtitle, palette, store="", icon=True):
    """An app's built site, as its own `make site` would leave it."""
    out = os.path.join(directory, "site")
    os.makedirs(os.path.join(out, "img"), exist_ok=True)
    if icon:
        open(os.path.join(out, "img", "icon-512.png"), "wb").close()
    locale = os.path.join(directory, "metadata", "en-US")
    os.makedirs(locale, exist_ok=True)
    with open(os.path.join(locale, "subtitle.txt"), "w", encoding="utf-8") as handle:
        handle.write(subtitle)
    return Site(
        chrome=Chrome(brand="Harbor&nbsp;Rush", icon="img/icon-512.png",
                      pages=PAGES, copyright="©"),
        out=out, metadata=os.path.join(directory, "metadata"),
        palette=palette, store=store,
        impressum={"app": "Harbor Rush", "name": "N", "street": "S",
                   "postcode": "1", "city": "C", "country": "D",
                   "phone": "+49 30 1", "email": "a@b.example"},
    )


with tempfile.TemporaryDirectory() as work:
    site = app_site(os.path.join(work, "harborrush"),
                    subtitle="Draw a route. Keep it flowing",
                    palette={"accent": "#ffd23f", "accent-ink": "#1d2a0a"})
    entry = portfolio.manifest(site)
    check("the card's name is the plain one, not the brand's markup",
          entry["name"] == "Harbor Rush")
    check("its slogan is the App Store subtitle, not a second one",
          entry["slogan"] == "Draw a route. Keep it flowing")
    check("it carries the app's own accent pair",
          (entry["accent"], entry["accent_ink"]) == ("#ffd23f", "#1d2a0a"))
    check("and the § 5 operator, so the root keeps no second copy of it",
          entry["operator"]["email"] == "a@b.example"
          and "app" not in entry["operator"])

    bare = app_site(os.path.join(work, "plain"), subtitle="A subtitle",
                    palette={})
    check("an app that overrides nothing still names the colour it renders in",
          portfolio.manifest(bare)["accent"] == assets.default_token("accent"))

    empty = app_site(os.path.join(work, "silent"), subtitle="", palette={})
    check("an empty subtitle fails the app's build, not the publish",
          raises(portfolio.manifest, empty))

    gone = app_site(os.path.join(work, "iconless"), subtitle="S", palette={},
                    icon=False)
    check("a card whose icon is not on disk fails the same way",
          raises(portfolio.manifest, gone))

with tempfile.TemporaryDirectory() as root:
    # A branch: two apps that have published, and a directory that has not.
    for slug, name, slogan, accent in (("zebra", "Zebra", "Last by name", "#111111"),
                                       ("apple", "Apple", "First by name", "#222222")):
        os.makedirs(os.path.join(root, slug, "img"))
        open(os.path.join(root, slug, "img", "icon.png"), "wb").close()
        for page_name in ("privacy.html", "support.html"):
            open(os.path.join(root, slug, page_name), "w").close()
        with open(os.path.join(root, slug, "app.json"), "w", encoding="utf-8") as handle:
            json.dump({"name": name, "slogan": slogan, "icon": "img/icon.png",
                       "icon_size": 512, "accent": accent, "accent_ink": "#fff",
                       "store": "",
                       "operator": {"name": "N", "street": "S", "postcode": "1",
                                    "city": "C", "country": "D",
                                    "phone": "+49 30 1",
                                    "email": "a@b.example"}}, handle)
    os.makedirs(os.path.join(root, "not-an-app"))

    found = portfolio.read_all(root)
    check("every app that has published is found, and only those",
          [slug for slug, _ in found] == ["apple", "zebra"])

    markup = portfolio.card("apple", dict(found)["apple"])
    check("a card links the directory it was found in", 'href="apple/"' in markup)
    check("it takes its app's colours inline",
          'style="--accent: #222222; --accent-ink: #fff"' in markup)
    check("with no store link, the way in is the app's own site",
          "Open site" in markup and "App Store" not in markup)

    with_store = portfolio.card("apple", dict(dict(found)["apple"],
                                              store="https://apps.apple.com/x"))
    check("a store link is offered when the app has one",
          'href="https://apps.apple.com/x"' in with_store)

    apps = portfolio.build(root, CONFIG)
    with open(os.path.join(root, "index.html"), encoding="utf-8") as handle:
        index = handle.read()
    check("the index is built from the branch, in name order",
          index.index("Apple") < index.index("Zebra"))
    check("it says what each app says about itself",
          "First by name" in index and "Last by name" in index)
    check("and nothing about the apps as a group",
          'class="lead"' not in index)
    check("the root's own pages and its mark are written",
          all(os.path.exists(os.path.join(root, name)) for name in
              ("index.html", "impressum.html", "style.css", "favicon.svg")))
    provider = open(os.path.join(root, "impressum.html"), encoding="utf-8").read()
    check("the § 5 identification names each app's own privacy policy",
          'href="apple/privacy.html"' in provider)
    check("its address is the one the apps publish, not one written here",
          "a@b.example" in provider and "Fraunhoferstr" not in provider)
    check("a built root passes its own checker", portfolio.check_root(root) == [])

    os.remove(os.path.join(root, "apple", "img", "icon.png"))
    check("a card pointing at something that is not there is caught",
          any("icon.png" in problem for problem in portfolio.check_root(root)))

with tempfile.TemporaryDirectory() as bare:
    check("an index with no apps on it is refused, not published empty",
          raises(portfolio.build, bare, CONFIG))

print()
if failures:
    print(f"{len(failures)} failed")
    sys.exit(1)
print("all tests passed")
