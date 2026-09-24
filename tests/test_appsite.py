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

from appsite import (Chrome, Page, Site, assets, badge, impressum, languages,
                     portfolio)
# Not `check`: this file's own assertion helper owns that name.
from appsite import check as site_check
from appsite.blocks import cards, hero, landing, section
from appsite.legal import (bullets, heading, mail, mail_href, muted, note, p,
                           render)

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
#: this package is imported by every app's repository and cannot pick their
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

header, _, _, _ = CHROME.render("en", "support.html")
check("with no store and no siblings, nothing outward is written",
      'class="away"' not in header and 'store-badge' not in header)

header, _, _, _ = CHROME.render("en", "support.html",
                                store="https://apps.apple.com/app/id1", more_apps="../")
check("the store is Apple's own badge at the top of an inner page",
      'href="https://apps.apple.com/app/id1"' in header
      and 'src="badge/app-store-en.svg"' in header)
check("and never a button this kit drew itself",
      "App&nbsp;Store" not in header and 'class="button' not in header)
check("the other apps are one link away", '<a class="away" href="../">More apps</a>' in header)

header, _, _, _ = CHROME.render("ja", "privacy.html",
                                store="https://apps.apple.com/app/id1", more_apps="../")
check("that link is written from a translated page's own depth",
      '<a class="away" href="../../">' in header)
check("and carries that language's label", "ほかのアプリ" in header)
check("the store link is not rewritten for depth",
      'href="https://apps.apple.com/app/id1"' in header)
check("but the badge beside it is, and speaks the page's language",
      'src="../badge/app-store-ja.svg"' in header)

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
    check("it carries the app's own accent",
          entry["accent"] == "#ffd23f")
    check("and no ink for it — nothing on a card is painted with the accent",
          "accent_ink" not in entry)
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
                       # `accent_ink` is a field cards published before the
                       # split still carry. It is here so the check below
                       # proves that a card ignores it rather than paints with it.
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
    check("it lights its own icon with its app's accent",
          'style="--card-accent: #222222"' in markup)
    check("and overrides no --accent, so every card's buttons are the page's",
          "--accent:" not in markup)
    check("with no store link, the way in is the app's own site",
          "Open site" in markup and "App Store" not in markup)

    with_store = portfolio.card("apple", dict(dict(found)["apple"],
                                              store="https://apps.apple.com/x"))
    check("a store link is offered when the app has one",
          'href="https://apps.apple.com/x"' in with_store)
    check("as Apple's badge, in the language of the page it sits on",
          'src="badge/app-store-en.svg"' in with_store
          and f'alt="{badge.ALT}"' in with_store)
    check("beside the same Open site button every other card has",
          'class="button"' in with_store and "ghost" not in with_store
          and "ghost" not in markup)

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

# ------------------------------------------------------- App Store field limits
#
# Connect rejects an over-length field at upload rather than truncating it, so
# without this the first you hear of it is a failed submission of a build that
# has already been made. One real overrun: a French subtitle at 31 against 30.

print("\nlisting limits")

with tempfile.TemporaryDirectory() as metadata:
    def locale(name, **fields):
        os.makedirs(os.path.join(metadata, name), exist_ok=True)
        for field, value in fields.items():
            with open(os.path.join(metadata, name, f"{field}.txt"), "w",
                      encoding="utf-8") as handle:
                handle.write(value + "\n")

    limited = Site(chrome=CHROME, out="site", metadata=metadata)

    locale("en-US", subtitle="Do a thing, quickly", keywords="a,b,c")
    locale("ja", subtitle="ちいさなことを、はやく")
    check("fields inside the limits pass",
          site_check.check_listing_limits(limited) == [])

    # 31 characters against 30 — the one that actually happened.
    locale("fr-FR", subtitle="Apprendre le morse, et le lacher")
    problems = site_check.check_listing_limits(limited)
    check("a subtitle one character over is caught",
          len(problems) == 1 and "fr-FR/subtitle.txt: 32" in problems[0])

    # Counted in characters, not bytes: eleven kana are eleven, and a check
    # that measured bytes would fail every CJK locale for being under.
    locale("ko", subtitle="가" * 31)
    check("length is characters, not bytes",
          any("ko/subtitle.txt: 31" in problem
              for problem in site_check.check_listing_limits(limited)))

    # review_information is App Review's private notes, not a listing.
    locale("review_information", subtitle="x" * 400)
    check("review_information is not measured as a listing",
          not any("review_information" in problem
                  for problem in site_check.check_listing_limits(limited)))

# ---------------------------------------------------------------- the template
#
# The README tells you to copy template/ and then run a recipe. For two apps the
# recipe named two scripts the template did not contain, so every app copied
# them from whichever sibling it happened to look at — and the docs said
# something that was not true of what they told you to copy. This is the check
# that keeps the two in step.

print("\ntemplate")

KIT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = KIT / "template"
README = (KIT / "README.md").read_text(encoding="utf-8")

recipe = {line.split("appstore/")[1].strip()
          for line in README.splitlines()
          if "python3 appstore/" in line and line.endswith(".py")}
check("the README's recipe names at least the five original scripts",
      len(recipe) >= 5)
missing = sorted(script for script in recipe if not (TEMPLATE / script).exists())
check(f"every script the README tells you to run is in template/{': missing ' + ', '.join(missing) if missing else ''}",
      not missing)

for script in sorted(TEMPLATE.glob("*.py")):
    try:
        ast.parse(script.read_text(encoding="utf-8"))
    except SyntaxError as error:
        check(f"template/{script.name} parses", False)
        break
else:
    check("every file in template/ parses", True)

# An app shipping in fewer languages than the kit knows is a config value, not
# a patch: JustTalk went out in English first, and before this the switcher and
# the hreflang links still advertised all eleven, so check_site counted eighty
# dead links against pages the build had never been asked to produce.
ONE = Site(chrome=Chrome(brand="App", icon="img/i.png", pages=PAGES, copyright="©"),
           out="site", languages=("en",))
check("a single-language site lists only its own language",
      ONE.chrome.language_codes() == ["en"])
check("the default is still every language the kit knows",
      SITE.chrome.language_codes() == list(languages.LANGUAGES))

header, footer, alternates, _ = ONE.chrome.render("en", "index.html")
others = [code for code in languages.LANGUAGES if code != "en"]
check("its switcher offers no language it was not built in",
      not any(f'"{code}/' in header or f"/{code}/" in header for code in others))
check("and it declares no hreflang alternate that does not exist",
      not any(f"{code}/" in alternates for code in others))

# Setting it on the Chrome directly still wins, so an app with a reason to
# differ is not locked out by the push-down above.
EXPLICIT = Site(chrome=Chrome(brand="App", icon="img/i.png", pages=PAGES,
                              copyright="©", languages=("en", "de")),
                out="site", languages=("en",))
check("an explicit Chrome language list is not overwritten",
      EXPLICIT.chrome.language_codes() == ["en", "de"])

# A landing page has nothing to inherit, so the template ships English only —
# and must stop rather than publish a site in one language.
landing = ast.parse((TEMPLATE / "make_site_translations.py").read_text(encoding="utf-8"))
table = next((node.value for node in ast.walk(landing)
              if isinstance(node, ast.Assign)
              and getattr(node.targets[0], "id", None) == "T"), None)
check("the template's landing copy is English only, so a build says what is missing",
      table is not None and [k.value for k in table.keys] == ["en"])

# And the template says which languages it ships in rather than letting the
# kit's table decide: the default is every language `appsite` knows, so an app
# that copies this file and translates eight of them advertises eleven, and
# check_site counts the other three as dead links. Naming the list here is
# also where an app deletes from.
config = ast.parse((TEMPLATE / "site_config.py").read_text(encoding="utf-8"))
site_call = next((node.value for node in ast.walk(config)
                  if isinstance(node, ast.Assign)
                  and getattr(node.targets[0], "id", None) == "SITE"), None)
declared = next((keyword.value for keyword in getattr(site_call, "keywords", ())
                 if keyword.arg == "languages"), None)
codes = [element.value for element in declared.elts] if declared is not None else []
check("the template declares its own language list",
      codes == list(languages.LANGUAGES))

print("\nthe support address")

# One mailbox serves every app, so a message that does not say which app it is
# about cannot be sorted — and until now each app wrote its own mailto: by
# hand. MorseHero shipped the template's support@example.com on its published
# terms page and JustTalk shipped a link with no subject at all; both are what
# happens when the address is written in an app rather than built from its
# config.
MAIL_SITE = Site(
    chrome=Chrome(brand="App", icon="img/i.png", pages=IMPRESSUM_PAGES, copyright="©"),
    out="site",
    impressum={"app": "Harbor Rush", "name": "N", "street": "S", "postcode": "1",
               "city": "C", "country": "D", "phone": "+49 30 1",
               "email": "a@b.example"},
)
check("the subject names the app, so a reply can be sorted",
      mail_href(MAIL_SITE) == "mailto:a@b.example?subject=Harbor%20Rush")
check("a topic is added to the app's name, never instead of it",
      mail_href(MAIL_SITE, "terms") == "mailto:a@b.example?subject=Harbor%20Rush%20terms")
check("the link reads as the address unless the caller says otherwise",
      mail(MAIL_SITE) == '<a href="mailto:a@b.example?subject=Harbor%20Rush">a@b.example</a>'
      and ">write to us<" in mail(MAIL_SITE, text="write to us"))

# An app whose mailbox is sorted by something other than its own name says so
# once, in its config, and every link on every page follows.
SUBJECT_SITE = Site(
    chrome=Chrome(brand="App", icon="img/i.png", pages=IMPRESSUM_PAGES, copyright="©"),
    out="site",
    impressum=dict(MAIL_SITE.impressum, subject="HR support"),
)
check("an explicit subject wins over the app's name",
      mail_href(SUBJECT_SITE) == "mailto:a@b.example?subject=HR%20support")

# The § 5 identification carries the same address, and built it separately
# until now. One seam: change the rule above and the Impressum follows.
check("the impressum writes the same link as every other page",
      mail_href(MAIL_SITE) in impressum.page(MAIL_SITE, "de"))

# The subject is the app's name, and there is one resolver for that name:
# `Site.name`. `mail_href` used to read `impressum["app"]` straight, which
# raised KeyError on a config without that key — which is every config the
# template ships — and would have put the brand's own markup in a subject
# line if an app had declared its § 5 name the way it declares its brand.
NAMELESS = Site(
    chrome=Chrome(brand="Harbor&nbsp;Rush", icon="img/i.png",
                  pages=IMPRESSUM_PAGES, copyright="©"),
    out="site",
    impressum={"name": "N", "street": "S", "postcode": "1", "city": "C",
               "country": "D", "phone": "+49 30 1", "email": "a@b.example"},
)
check("a config with no app name falls back to the brand rather than raising",
      NAMELESS.name == "Harbor Rush"
      and mail_href(NAMELESS) == "mailto:a@b.example?subject=Harbor%20Rush")
check("and the brand's markup never reaches a subject line",
      "nbsp" not in mail_href(NAMELESS))
check("the § 5 name still wins when there is one",
      MAIL_SITE.name == "Harbor Rush")
check("the page title and the mail subject read the same name",
      Site(chrome=MAIL_SITE.chrome, out="site",
           impressum=dict(MAIL_SITE.impressum, app="Other")).name == "Other")

# The template is what a new app copies, and a placeholder address that still
# resolves as a link is the one kind of TODO nothing catches later.
legal_src = (TEMPLATE / "make_site_legal.py").read_text(encoding="utf-8")
support_src = (TEMPLATE / "site_text_support.py").read_text(encoding="utf-8")
check("the template writes no address of its own",
      "support@example.com" not in legal_src
      and '"mailto:' not in legal_src and '"mailto:' not in support_src)
check("and its support page takes the contact from the kit",
      "{contact}" in support_src)

print("\nthe copyright line")

# Six listings carried three spellings of one line. It is checked rather than
# remembered because nobody reads six listings side by side.
with tempfile.TemporaryDirectory() as metadata:
    os.makedirs(os.path.join(metadata, "en-US"))
    SAME = Site(chrome=Chrome(brand="App", icon="img/i.png", pages=PAGES,
                              copyright="©"), out="site", metadata=metadata)
    check("a missing copyright line is a problem, not a silence",
          any("copyright.txt" in problem for problem in site_check.check_copyright(SAME)))

    with open(os.path.join(metadata, "copyright.txt"), "w", encoding="utf-8") as handle:
        handle.write(site_check.COPYRIGHT + "\n")
    check("the house line passes, trailing newline and all",
          site_check.check_copyright(SAME) == [])

    with open(os.path.join(metadata, "copyright.txt"), "w", encoding="utf-8") as handle:
        handle.write("Copyright 2026 Igor Kunin\n")
    check("and another spelling of the same claim does not",
          len(site_check.check_copyright(SAME)) == 1)

    # A Mac app keeps it under a platform directory, which is where deliver
    # looks for it; the check follows rather than insisting on one layout.
    os.remove(os.path.join(metadata, "copyright.txt"))
    os.makedirs(os.path.join(metadata, "mac"))
    with open(os.path.join(metadata, "mac", "copyright.txt"), "w", encoding="utf-8") as handle:
        handle.write(site_check.COPYRIGHT + "\n")
    check("found under a platform directory too", site_check.check_copyright(SAME) == [])

print("\nplaceholders that got published")

# A reserved domain cannot be a real destination, so one on a built page is a
# TODO that rendered as a working link. The checker is the seam: every app
# runs it at the end of `make site`, and nobody has to remember which of the
# template's constants they were supposed to edit.
check("a reserved domain is found, and clean markup is left alone",
      site_check.placeholders('<a href="https://example.com/">Sound</a>') == ["example.com"]
      and site_check.placeholders('<a href="mailto:a@b.example">a</a>') == [])

with tempfile.TemporaryDirectory() as out:
    with open(os.path.join(out, "terms.html"), "w", encoding="utf-8") as handle:
        handle.write('<title>Terms</title>'
                     '<p>Sounds from <a href="https://example.com/">MuseScore_General</a>.</p>')
    LEFTOVER = Site(chrome=Chrome(brand="App", icon="img/i.png", pages=PAGES,
                                  copyright="©"), out=out)
    problems, pages = site_check.check_pages(LEFTOVER, required=(), impressum=None)
    check("and the build stops on it rather than publishing the page",
          pages == 1 and any("placeholder" in problem for problem in problems))

# The family list is the count: a name missing from it is a name this check
# cannot see on another app's page. JustTalk published while it was absent.
check("an app that joined the family is caught on another app's page",
      site_check.other_apps_named("<p>Made with JustTalk</p>", "MorseHero") == ["JustTalk"]
      and site_check.other_apps_named("<p>Made with JustTalk</p>", "JustTalk") == [])

# ------------------------------------------------------- Apple's own artwork

print("\nthe App Store badge")

check("every language this kit builds in has artwork to show",
      set(badge.LOCALES) == set(languages.LANGUAGES))
check("and the file for each one is committed, not fetched at build time",
      all(os.path.exists(os.path.join(badge.ARTWORK, f"app-store-{code}.svg"))
          for code in badge.LOCALES))

# Apple's exports are not one shape. Drawing them all in a box measured from
# the English one would squeeze Korean and stretch Japanese — which is exactly
# the "don't modify the badge" the guidelines open with.
check("each badge is measured at Apple's 40 px minimum, not assumed",
      badge.box("en") == (120, 40) and badge.box("ja") == (109, 40)
      and badge.box("ko") == (130, 40))
check("the words on it are never ours to translate",
      badge.ALT == "Download on the App Store")

with tempfile.TemporaryDirectory() as out:
    OFF_STORE = Site(chrome=CHROME, out=out)
    check("an app that is not on the store carries no badge",
          badge.install(OFF_STORE) == [] and not os.path.exists(
              os.path.join(out, badge.DIRECTORY)))

with tempfile.TemporaryDirectory() as out:
    LIVE = Site(chrome=CHROME, out=out, store="https://apps.apple.com/app/id1",
                languages=("en", "de"))
    # Through `assets.install`, which is what every app's build already calls:
    # the badge arrives with the stylesheet, so no app repository needed a new
    # step and none can be left drawing its own button.
    assets.install(LIVE)
    written = badge.install(LIVE)
    check("the stylesheet install is what puts it there",
          os.path.exists(os.path.join(out, badge.file("de"))))
    check("a live one carries the artwork for its own languages, and no more",
          len(written) == 2
          and sorted(os.listdir(os.path.join(out, badge.DIRECTORY)))
          == ["app-store-de.svg", "app-store-en.svg"])
    check("installed byte for byte, as the guidelines require",
          open(os.path.join(out, badge.DIRECTORY, "app-store-de.svg"), "rb").read()
          == open(os.path.join(badge.ARTWORK, "app-store-de.svg"), "rb").read())


print()
if failures:
    print(f"{len(failures)} failed")
    sys.exit(1)
print("all tests passed")
