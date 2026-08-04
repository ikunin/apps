"""The page at the root of the Pages site: every app that has published one.

One GitHub Pages site serves three apps, a directory each, and its root said
"Nothing here" until this existed. This is that root — a card per app, each
carrying the app's icon, its name and the one-line slogan it already ships on
the App Store.

**Nothing here is a list somebody keeps up to date.** Each app's build writes an
`app.json` into its own `site/`; publishing copies that up with the pages; this
module then rebuilds the index from whatever manifests are on the branch. An app
that has published is on the page. One that has not, is not. A fourth app needs
no edit here at all — it publishes, and it is there.

**What a card may say is deliberately narrow.** The app's own icon, name and
subtitle, and a link into its own site. No counts, no aggregate sentence about
"the apps". The three differ in what they collect — one ships analytics, one
ships nothing — and a sentence written about all of them at once is a sentence
that is false about at least one. That has already been published once; see
AGENTS.md.
"""

import dataclasses
import html
import importlib.util
import json
import os

from . import assets, check, impressum, listing
from .blocks import button, hero

#: What an app leaves in its own site directory for this page to read.
MANIFEST = "app.json"

#: The § 5 fields that describe the operator rather than the app. One operator,
#: one address: the root's Impressum takes these from the apps rather than
#: keeping a fourth copy of an address that is already in three site_config.py
#: files. `app` and `subject` are not here — those name an app.
OPERATOR = impressum.REQUIRED + ("vat",)

_ASSETS = os.path.join(os.path.dirname(__file__), "assets")
STYLES = os.path.join(_ASSETS, "portfolio.css")
FAVICON = os.path.join(_ASSETS, "favicon.svg")

#: The kit's own configuration for this page — brand, hero line, palette and
#: the § 5 address — sitting beside the package rather than inside it, exactly
#: as each app's `site_config.py` sits beside its repository's build scripts.
CONFIG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "portfolio_config.py")


# ------------------------------------------------------------ the manifest ---

def plain(brand):
    """`Harbor&nbsp;Rush` as a person would type it.

    `Chrome.brand` is markup — it carries a non-breaking space so the name
    cannot wrap in the header — and a card needs the name as text.
    """
    return html.unescape(brand).replace("\xa0", " ").strip()


def manifest(site):
    """What one app tells the portfolio about itself.

    Every field is read from something the app already maintains, so a card
    cannot drift from the app: the name from the § 5 block, the slogan from the
    App Store listing, the icon and the accent from the site's own config.
    Writing a second slogan here would be a second thing to keep in step.
    """
    name = plain(site.impressum.get("app") or site.chrome.brand)
    slogan = listing.read(site, "en", "subtitle")
    icon = os.path.join(site.out, site.chrome.icon)
    if not name:
        raise SystemExit("this app has no name — set Site.impressum['app']")
    if not slogan:
        raise SystemExit("subtitle.txt is empty, and it is the card's slogan")
    if not os.path.exists(icon):
        raise SystemExit(f"{icon}: the card's icon is not there")
    return {
        "name": name,
        "slogan": slogan,
        "icon": site.chrome.icon,
        "icon_size": site.chrome.icon_size,
        # The colours this app's own site renders in — its overrides, or the
        # stylesheet's defaults when it has none. Both, because a button is an
        # accent background with accent-ink on it, and half a pair is a
        # yellow button with white text on it.
        "accent": site.palette.get("accent") or assets.default_token("accent"),
        "accent_ink": (site.palette.get("accent-ink")
                       or assets.default_token("accent-ink")),
        "store": site.store,
        # The whole token table, not just the accent: the root wears one app's
        # colours (see PALETTE_FROM in portfolio_config.py) and follows it from
        # here rather than keeping a second copy of it to fall behind.
        "palette": dict(site.palette),
        # The § 5 operator, so the root's Impressum can be built without a
        # second copy of an address that lives in this app's site_config.py
        # and nowhere else. Everything here is already on 45 published pages.
        "operator": {key: site.impressum[key] for key in OPERATOR
                     if site.impressum.get(key)},
    }


def write(site):
    """Write this app's card into its own site directory. Returns the path.

    It rides onto the branch with the pages: `publish.py` copies `site/`
    wholesale, so this lands at `<app>/app.json` with no plumbing of its own.
    """
    path = os.path.join(site.out, MANIFEST)
    os.makedirs(site.out, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(manifest(site), handle, ensure_ascii=False, indent=2,
                  sort_keys=True)
        handle.write("\n")
    return path


def read_all(root):
    """Every app that has published, as (directory, manifest), by name.

    The directory it was found in *is* the app's URL, so there is no slug in
    the manifest to disagree with where the files actually are.
    """
    found = []
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name, MANIFEST)
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as handle:
                found.append((name, json.load(handle)))
    return sorted(found, key=lambda app: app[1]["name"].lower())


# ---------------------------------------------------------------- the page ---

#: The two things a card can invite you to do. Not translated: this page is
#: English, and each card leads into a site that is not.
OPEN = "Open site"
STORE = "App Store"


def card(slug, app):
    """One app. Its icon, its name, its own slogan, and the way in."""
    # The card's own accent overrides the token for everything inside it, so
    # the button and the icon's halo come out in the app's colour without a
    # line of per-app CSS. The pair travels together: the ink is what is
    # legible *on* that accent, and the page's own would not be.
    tokens = [f"--{name}: {app[key]}"
              for name, key in (("accent", "accent"), ("accent-ink", "accent_ink"))
              if app.get(key)]
    style = f' style="{"; ".join(tokens)}"' if tokens else ""
    size = app.get("icon_size", 512)
    store = app.get("store")
    buttons = [button(OPEN, f"{slug}/", ghost=bool(store))]
    if store:
        buttons.insert(0, button(STORE, store))
    return (f'    <div class="app"{style}>\n'
            f'      <img src="{slug}/{app["icon"]}" alt="" '
            f'width="{size}" height="{size}" loading="lazy">\n'
            f'      <h3><a href="{slug}/">{html.escape(app["name"])}</a></h3>\n'
            f'      <p>{html.escape(app["slogan"])}</p>\n'
            f'      <div class="actions">{"".join(buttons)}</div>\n'
            '    </div>\n')


def body(config, apps):
    """<main> for the index: the hero, then the apps."""
    grid = "".join(card(slug, app) for slug, app in apps)
    return ("<main>\n\n"
            + hero(headline=config.HERO, lead=config.LEAD)
            + '\n<div class="wrap">\n\n<section>\n'
            f'  <div class="apps">\n{grid}  </div>\n'
            "</section>\n</div>\n</main>\n")


def operator(apps):
    """The § 5 provider, as the published apps report it.

    One operator, one address. Taking it from the apps means a move is still
    one edit per app repository and none here — and it means this page cannot
    quietly go on naming an address the apps have stopped using.
    """
    blocks = [(slug, app["operator"]) for slug, app in apps if app.get("operator")]
    if not blocks:
        raise SystemExit(
            "no published app carries a § 5 operator block — rebuild an app "
            "with make_site_card.py, or the root would have no Impressum")
    first, block = blocks[0]
    for slug, other in blocks[1:]:
        if other != block:
            print(f"  warn {slug} and {first} disagree about the operator's "
                  "address; using " + first)
    return block


def borrowed_palette(config, apps):
    """The colours of the app this page dresses as, or nothing.

    This page belongs to no app, so it has to take *some* palette, and the
    kit's default is TappyMusic's. Naming one app and reading its tokens off
    the card it publishes keeps the root in step with that app's own site:
    restyle the app, republish, and this follows.
    """
    wanted = getattr(config, "PALETTE_FROM", "")
    if not wanted:
        return {}
    for slug, app in apps:
        if slug != wanted:
            continue
        if app.get("palette"):
            return app["palette"]
        print(f"  warn {wanted}'s card carries no palette — rebuild it with "
              "make_site_card.py; the index is in the kit's colours meanwhile")
        return {}
    print(f"  warn {wanted} has not published a card, so the index cannot take "
          "its colours; using the kit's own")
    return {}


def site_at(config, root, apps):
    """The config's `Site`, pointed at the directory being written.

    Its § 5 block is the operator the apps report, under the name and mail
    subject this page uses — the only two of those fields that describe a site
    rather than a person. Its colours are the app named in the config.
    """
    site = dataclasses.replace(config.SITE, out=root,
                               impressum={**operator(apps), **config.IMPRESSUM})
    palette = borrowed_palette(config, apps)
    if not palette:
        return site
    # The address bar takes the same background the page does.
    return dataclasses.replace(site, palette=palette,
                               theme_color=palette.get("bg", site.theme_color))


def index(config, site, apps):
    return site.document("en", "index.html", title=config.TITLE,
                         description=config.DESCRIPTION, main=body(config, apps))


def provider(config, site, apps):
    """The root's Impressum: the same § 5 block every app page carries.

    Its DSGVO paragraph names each app's own privacy page rather than one of
    its own, because this page has none — and its note sends a reader to the
    support page of whichever app they came for.
    """
    def named(page):
        return ", ".join(f'<a href="{slug}/{page}">{html.escape(app["name"])}</a>'
                         for slug, app in apps)

    # The same two paragraphs an app's Impressum carries, in the plural: this
    # page sells nothing itself and has no policy of its own, so both point at
    # the apps rather than at pages beside it.
    about = ("""  <h3>Verkauf über den App&nbsp;Store</h3>
  <p>
    Die Apps und alle In-App-Käufe werden über den Apple App&nbsp;Store
    vertrieben. Vertragspartner für den Kauf ist Apple; Rückerstattungen
    laufen über
    <a href="https://reportaproblem.apple.com">reportaproblem.apple.com</a>.
  </p>

  <h3>Datenschutz</h3>
  <p>
    Verantwortlicher im Sinne der DSGVO ist der oben genannte Diensteanbieter.
    Diese Seite verweist nur auf die Apps; jede App hat ihre eigene
"""
             f"    Datenschutzerklärung: {named('privacy.html')}.\n  </p>\n")
    note = config.IMPRESSUM_NOTE.format(support=named("support.html"))
    return impressum.page(site, "en", about=about, note=note)


# --------------------------------------------------------------- the build ---

def load_config(path=CONFIG):
    """The root's own config, by path rather than by import.

    It sits beside the package, not inside it, so it is not importable as
    `appsite.portfolio_config` — and an app repository that vendors the kit must
    not have to put the kit's own root on its `sys.path` to publish.
    """
    if not os.path.exists(path):
        raise SystemExit(f"{path}: the portfolio's configuration is not there")
    spec = importlib.util.spec_from_file_location("portfolio_config", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"{path}: the portfolio's configuration is not there")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def install(site):
    """The root's stylesheet and its mark.

    The card rules are appended to the kit's own stylesheet rather than served
    beside it: one file, one request, and no chance of the two disagreeing
    about a token. They come after the palette, and name tokens rather than
    colours, so the page comes out in whatever the palette says.
    """
    target = assets.install(site)
    with open(STYLES, encoding="utf-8") as handle:
        card_rules = handle.read()
    with open(target, "a", encoding="utf-8") as handle:
        handle.write("\n" + card_rules)
    with open(FAVICON, encoding="utf-8") as handle:
        mark = handle.read()
    # The mark is four tiles in the page's own colours, so it cannot be a flat
    # file: it is the one asset that has to know the palette.
    for token, default in (("bg-2", "#0e0c19"), ("accent", "#c7b9ff"),
                           ("cyan", "#7fd8f7"), ("pink", "#ff9ec4"),
                           ("violet", "#c7b9ff")):
        mark = mark.replace("{%s}" % token,
                            site.palette.get(token) or assets.default_token(token)
                            or default)
    with open(os.path.join(site.out, "favicon.svg"), "w", encoding="utf-8") as handle:
        handle.write(mark)


def build(root, config=None):
    """Write the index, the Impressum, the stylesheet and the mark into `root`.

    Returns the apps it found. Everything it writes is derived from them, so
    building twice over the same branch produces the same bytes.
    """
    config = config or load_config()
    apps = read_all(root)
    if not apps:
        raise SystemExit(
            f"{root}: no {MANIFEST} anywhere — no app has published a card, "
            "and an index with nothing on it is worse than none")
    site = site_at(config, root, apps)
    install(site)
    for name, markup in (("index.html", index(config, site, apps)),
                         ("impressum.html", provider(config, site, apps))):
        with open(os.path.join(root, name), "w", encoding="utf-8") as handle:
            handle.write(markup)
    return apps


def check_root(root):
    """The root's own pages hold together. The app directories check themselves.

    Same rules the app sites are held to, and the same parser — a link that
    resolves, alt text on every image, a title — but only over the files this
    module wrote. Walking into the app directories would re-check 136 pages
    that each app's own build already checked.
    """
    problems = []
    pages = sorted(name for name in os.listdir(root) if name.endswith(".html"))
    for page in pages:
        with open(os.path.join(root, page), encoding="utf-8") as handle:
            markup = handle.read()
        parser = check.Links()
        parser.feed(markup)
        for value, line in parser.found:
            target = check.local_target(value)
            if target is None:
                continue
            if not os.path.exists(os.path.normpath(os.path.join(root, target))):
                problems.append(f"{page}:{line}: {value} does not exist")
        for _ in check.images_without_alt(markup):
            problems.append(f"{page}: an <img> has no alt text")
        if "<title>" not in markup:
            problems.append(f"{page}: no <title>")
    return problems
