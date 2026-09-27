# Maintaining the app sites

Instructions for an AI agent — Claude Code, Gemini CLI, or any other — working
on the websites for TappyMusic, Harbor Rush, SpeedyCards, VideoSqueezer and
MorseHero.

`CLAUDE.md` and `GEMINI.md` in this repository both point here. This file is
the one that is maintained; do not copy it.

---

## What exists

One GitHub Pages site, one directory per app, eleven languages each, and an
index at the root that lists them — the apps are named in `FAMILY` in
`appsite/check.py`, which is the list to read rather than a number written
here, because a number written here is wrong the next time one publishes:

```
https://ikunin.github.io/apps/                 the index — generated, see below
https://ikunin.github.io/apps/tappymusic/      66 pages
https://ikunin.github.io/apps/harborrush/      55 pages
https://ikunin.github.io/apps/speedycards/     55 pages
https://ikunin.github.io/apps/videosqueezer/   55 pages
https://ikunin.github.io/apps/morsehero/       55 pages
```

Five pages in each of eleven languages — landing, support, privacy, terms and
Impressum — and TappyMusic carries a sixth, `songs.html`. These counts are what
was on `gh-pages` on 20 September 2026; nothing reads them, so they go stale
quietly.

Served from the **`gh-pages` branch of this repository**. `main` is the kit —
code, template, tests, and this file.

**The split is the design, and it is not symmetric.** Structure is shared
because a bug in it is one bug. Prose is owned by each app because a privacy
policy is a promise about one particular program, and a sentence that has to
change for one app must not change for the others.

| Shared, here in `appsite/` | Owned, in each app's repository |
|---|---|
| Navigation, language switcher, `hreflang` (`chrome.py`) | Which pages exist, brand, icon (`site_config.py`) |
| The document and its `<head>` (`site.py`) | Which blocks, in what order |
| Page blocks — hero, cards, showcase, note, lockup, stats (`blocks.py`) | Every word of the landing copy (the `T` table) |
| Legal-page shape (`legal.py`) | Every sentence of support, privacy, terms |
| The stylesheet (`assets/style.css`) | Its palette, as token overrides |
| The checkers (`check.py`, `check_text.py`) | What the listing must point at |
| The publish step (`publish.py`) | — |
| The index of the apps (`portfolio.py`, `portfolio_config.py`) | Its card (`site/app.json`) |

## Where each app keeps its words

Two paths, the same in every repository: the kit is the submodule at
**`vendor/appsite`**, and that app's own words are in **`appstore/`**. Both
lowercase — `Tools/` and `tools/` are the same directory on a case-insensitive
Mac and two different ones on Linux CI. Every app builds with `make site`.

In `appstore/`: `site_config.py` (the whole interface to the kit),
`make_site_translations.py` (landing page + the `T` table),
`site_text_{support,privacy,terms}.py`, `make_site_card.py`, and generated
`site/` at the repository root.

These directories used to be `Tools/appstore/`, `docs/appstore/` and
`scripts/site/` — one name each, for no reason. If you find a doc still saying
so, it is stale.

---

## Recipes

### Change a sentence

Edit the `"en"` entry **and every translation of that sentence**, then
`make site`. There is no test that can tell you a translation has fallen
behind its English — only a person reading both.

### Change how a page is shaped

That belongs in the kit and lands on every app.

```sh
cd vendor/appsite && python3 tests/test_appsite.py
cd - && make site && git diff --stat site/      # expect only what you intended
```

The kit's own gate is that a shipped site re-renders **byte-identically**
unless you meant to change it. Run `make site` in every app after any kit
change and read the diff.

### Publish

```sh
make site                                            # build and check
python3 vendor/appsite/publish.py --app <app>        # copy onto gh-pages
```

`--dry-run` reports without pushing. Publishing one app replaces only its own
subdirectory, so it cannot take another app down. Pages takes about a minute.

**Never edit the `gh-pages` branch directly.** It is output. The next publish
overwrites it — including the index at the root.

### Change the index at the root

`ikunin.github.io/apps/` lists the apps, and is rebuilt from the branch on
every publish: each app's `make site` writes `site/app.json`, publishing
carries it up, and `portfolio.py` reads every one it finds. So —

- **an app missing from the index has not been rebuilt** since `app.json`
  existed. Run its `make site` and publish it.
- **its card changed on its own?** Something in that app's `site_config.py` or
  its `subtitle.txt` changed. The card has no words of its own.
- **the page's own wording, colours and § 5 address** are in
  `portfolio_config.py` here. After editing it:

```sh
python3 vendor/appsite/publish.py --index-only --dry-run
```

**A card is an icon, a name and that app's own App Store subtitle.** Do not add
a sentence about the apps to that page. They differ in what they collect, and
one sentence about all of them is a false statement about at least one —
which is the mistake below, in a place where it would be published fastest.

**Every card's buttons are the page's colour; only its icon is the app's.** A
card carries its app's accent as `--card-accent`, and that reaches two things:
the halo under its icon and its hover edge. A warmth per app, so the grid does
not read as one grey list.

A card must **never** set `--accent`. That token paints `.button`, it cascades
into everything inside the card, and a differently-coloured way in per app
reads as separate sites side by side rather than as one shelf — which is how
the page
shipped until it was fixed. The index's own `--accent` is one colour for the
whole page: whatever `PALETTE_FROM` in `portfolio_config.py` names.

The rule lives in `portfolio.card()`, the two tokens are split in
`assets/portfolio.css`, and `tests/test_appsite.py` fails if a card writes
`--accent` again.

### Add a language

`languages.py` in the kit: add a `Language` with its endonym, App Store
locale, navigation labels and governing-language clause. Then every app's text
tables need that language, and its `metadata/<locale>/` must exist. Apple's
badge locale goes in `badge.LOCALES` — theirs is spelled differently from App
Store Connect's — and `python3 refresh_badges.py` fetches the artwork.

### Put an app on the store

One line: `store="https://apps.apple.com/app/id<n>"` in that app's
`site_config.py`. The header of all of its pages and its card on the index then
carry **Apple's own badge**, in each page's language, installed with the
stylesheet. Empty until the app is live, and nothing is drawn.

**Never draw the way into the store.** Apple's marketing guidelines ask that
nobody recreate the badge, restyle it, stretch it or translate the words on it
— and *App Store* is a mark that stays in English everywhere, alt text
included. This kit shipped a little accent-coloured pill reading "App Store"
for a year, which was all four mistakes in one element. The rules now live in
`appsite/badge.py`: 40 px tall, a quarter of that in clear space, the black
badge, the artwork's own width per language (Japanese 109 px, Korean 130), and
one badge per layout. `link()` there is the only place either surface builds
one.

### Put an app on several stores

An app that ships as several records, or on Windows, names them all instead:
`stores=(("ios", url), ("mac", url), ("windows", url))`, in the order they
should be offered. Each wears **its store's own badge** — Apple's for `ios
iphone ipad mac tv watch`, Microsoft's "Download from the Microsoft Store" for `windows` —
and the kit draws no button for any store. More than one live, and each is
named for its device. An empty url is a platform not live yet: the header and
the index card write nothing for it, and an app's own download section can show
it with `stores.way()` — the badge unlinked and dimmed, "coming soon" beneath,
in the page's language. `appsite/stores.py` is the one renderer; `badge.py`
holds each store's artwork source and alt text, and `refresh_badges.py` fetches
both stores' eleven files. `app.json` carries `stores` only for an app that
sets it, so a single-store app's card does not move.
