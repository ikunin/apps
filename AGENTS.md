# Maintaining the app sites

Instructions for an AI agent — Claude Code, Gemini CLI, or any other — working
on the websites for TappyMusic, Harbor Rush and SpeedyCards.

`CLAUDE.md` and `GEMINI.md` in this repository both point here. This file is
the one that is maintained; do not copy it.

---

## What exists

One GitHub Pages site, three apps, eleven languages each:

```
https://ikunin.github.io/apps/tappymusic/     46 pages
https://ikunin.github.io/apps/harborrush/     45 pages
https://ikunin.github.io/apps/speedycards/    45 pages
```

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

## Where each app keeps its words

The submodule is at **`vendor/appsite`** in every repository — not `Tools/`,
not `tools/`, which are the same directory on a case-insensitive Mac and two
different ones on Linux CI.

| App | Text tables | Build |
|---|---|---|
| TappyMusic | `Tools/appstore/` | `make site` |
| Harbor Rush | `docs/appstore/` | `make site` |
| SpeedyCards | `scripts/site/` | `make site` |

In each: `site_config.py` (the whole interface to the kit),
`make_site_translations.py` (landing page + the `T` table),
`site_text_{support,privacy,terms}.py`, and generated `site/`.

---

## Recipes

### Change a sentence

Edit the `"en"` entry **and every translation of that sentence**, then
`make site`. There is no test that can tell you a translation has fallen
behind its English — only a person reading both.

### Change how a page is shaped

That belongs in the kit and lands on all three apps.

```sh
cd vendor/appsite && python3 tests/test_appsite.py
cd - && make site && git diff --stat site/      # expect only what you intended
```

The kit's own gate is that a shipped site re-renders **byte-identically**
unless you meant to change it. Run `make site` in all three apps after any
kit change and read the diff.

### Publish

```sh
make site                                            # build and check
python3 vendor/appsite/publish.py --app <app>        # copy onto gh-pages
```

`--dry-run` reports without pushing. Publishing one app replaces only its own
subdirectory, so it cannot take another app down. Pages takes about a minute.

**Never edit the `gh-pages` branch directly.** It is output. The next publish
overwrites it.

### Add a language

`languages.py` in the kit: add a `Language` with its endonym, App Store
locale, navigation labels and governing-language clause. Then every app's text
tables need that language, and its `metadata/<locale>/` must exist.

---

## What goes wrong

Every item here has already happened once.

**Never copy a privacy or terms claim between these apps.** They differ in
ways that make a copied sentence a false statement:

| | TappyMusic | Harbor Rush | SpeedyCards |
|---|---|---|---|
| `PrivacyInfo.xcprivacy` | collects nothing | `ProductInteraction`, unlinked | collects nothing |
| Analytics | none | TelemetryDeck linked | TelemetryDeck linked, App ID empty |
| iCloud | no | no | streaks and XP in the user's KVS |
| Age rating | 4+ | 9+ | not a children's app |

"No analytics, no data leaves the device" was written into Harbor Rush's
landing page in eleven languages before anyone checked its privacy manifest.
SpeedyCards' privacy policy described *melody packs and cliparts*, and claimed
the app was "designed for children and rated 4+", and was live that way.

**A blanket rename renames the app, not what the app is about.** Replacing
`TappyMusic` with `SpeedyCards` across a file leaves "a particular song" and
"melody packs" in place, wearing the new name. `check_text.py` looks for this.

**Run both checkers before publishing.**

```sh
python3 vendor/appsite/check_text.py --texts <text dir> --app <app>
make site        # runs check_site.py
```

`check_text.py` catches out-of-script characters — Cyrillic inside Japanese,
Korean inside Japanese — which read as fine to anyone who does not read that
language. It has found four such bugs, two of them already published.

**Listing URLs are per-locale and every one must resolve.** Each locale points
at its own `<lang>/support.html`. `check_site.py` resolves all 33 per app
against the files on disk. Verify the live ones after publishing:

```sh
for f in <metadata>/*/{marketing,support,privacy}_url.txt; do
  curl -s -o /dev/null -w "%{http_code} $(cat $f)\n" "$(cat $f)"; done
```

**The kit must parse on Python 3.11.** A backslash inside an f-string
expression is legal from 3.12 and a `SyntaxError` before it; the package
imported fine locally and could not be imported at all by CI. The test suite
now checks every file with `ast.parse(feature_version=(3, 11))`.

**`site/` is generated.** Only `site/impressum.html` is written by hand.
Everything else, `style.css` included, is overwritten on the next build.

**Never publish a private email address.** Harbor Rush's old site published
one. Every app now shares one contact address, `support.kunin@gmail.com`, and
the `mailto:` subject names the app so replies can be sorted.

---

## Checks that must pass

```sh
cd vendor/appsite && python3 tests/test_appsite.py    # kit: syntax floor, chrome, blocks
python3 vendor/appsite/check_text.py --texts <dir> --app <app>
make site                                             # links, alt text, listing URLs
```

## What needs a human, not an agent

- **Creating the support mailbox.** `support.kunin@gmail.com` is the shared
  address on every app's live pages. Confirm it exists before publishing.
- **Deciding whether an app ships analytics.** Setting a TelemetryDeck App ID
  changes the privacy policy, the App Store privacy label and the landing copy
  in eleven languages. Ask; do not infer it from the code.
- **The Impressum.** § 5 DDG, a real address and telephone number, and the one
  hand-written page. Do not generate it.
- **Judging a translation.** The checkers catch mechanical faults. Nothing here
  can tell you whether the German reads well.
