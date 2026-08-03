# appsite

One implementation of an App Store companion site, in eleven languages.

A small app on the store needs the same pages every time: what it is, support,
a privacy policy, terms, and — for a German operator — an Impressum. In eleven
languages that is 45 files. Writing them twice is how the second app ends up
wearing the first app's navigation, and how a fix to the checker lands on one
app and rots on the others.

**This package holds the structure. Each app holds its own words.**

## What is in here, and what is not

| Here (shared) | In the app (owned) |
|---|---|
| Navigation, language switcher, `hreflang` | The app's name, brand markup, icon |
| The document: `<head>`, assets, `<main>` | Which pages exist, and any page the kit does not know about |
| Page blocks: hero, cards, showcase, note, lockup, stats | Which blocks, in what order, with what copy |
| Legal-page structure and the standard Apple links | Every sentence of the privacy policy and terms |
| The stylesheet | Its palette, as token overrides |
| The checker | What the listing is required to point at |

The split is not arbitrary. **Structure is single-sourced because a bug in it is
one bug.** **Prose is owned because a sentence that has to change for one app
must not change for the others** — a privacy policy is a promise about a
particular program, and sharing the text would eventually make one of the
promises false.

## Use it

Add the kit as a submodule and write one config file:

```sh
git submodule add <url> Tools/appsite
cp Tools/appsite/template/* Tools/appstore/
```

`site_config.py` is the whole interface:

```python
SITE = Site(
    chrome=Chrome(brand="Harbor&nbsp;Rush", icon="img/icon-512.png",
                  pages=PAGES, copyright="© Igor Kunin 2026"),
    out="site",
    metadata=os.path.join("fastlane", "metadata"),
    palette={"accent": "#1ec8b6"},
)
```

Then, in the app's Makefile:

```make
site:
	python3 Tools/appstore/install_site_assets.py
	python3 Tools/appstore/make_site_translations.py
	python3 Tools/appstore/make_site_legal.py
	python3 Tools/appstore/check_site.py
```

## The listing is the source of the pitch

The landing page's headline and opening paragraph are read from
`metadata/<locale>/subtitle.txt` and `description.txt` — fastlane's layout,
which App Store Connect's own tools also expect. Those words are already
translated and already reviewed, and they are what a customer meets before they
ever reach the site. Translating the same pitch twice guarantees the two drift.

## Translating a page

`languages.py` carries what is the same for every app: language names,
navigation labels for the five standard pages, and the governing-language
clause. A page kind the kit does not know needs its own labels on the `Page` —
that is the seam that keeps "Songs" out of a site kit.

Every translated privacy and terms page ends with a line saying the English
version governs, linking back to it. A promise that reads differently in two
languages is a legal problem; this resolves it in the open rather than hiding
it.

## `template/`

A starting point to copy into an app, not a dependency. The legal text tables
come from a real shipped app, so most of the eleven-language work is already
done — but **each file's header lists the keys that describe that app and must
be rewritten.** Read them. A privacy policy inherited without reading is worse
than no policy.

## Tests

```sh
python3 -m pytest tests
```

The kit's own gate, when it was extracted, was that it re-rendered a shipped
46-page site byte-identically. That is the check to repeat after changing
anything here: build the app's site, `git diff`, and expect nothing.
