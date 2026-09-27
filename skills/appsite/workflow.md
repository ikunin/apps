# /appsite — add an App Store companion site

Build the eleven-language site an app on the store needs — home, support,
privacy, terms, Impressum — from `github.com/ikunin/appsite`, translate the App
Store listing to match, and publish to `ikunin.github.io/apps/<slug>/`.

**The failure mode of this skill is publishing another app's promises.** The
kit's template legal text is a real, shipped policy for a *different* program.
Copied unread it becomes a false statement about this one, in eleven languages,
on the open web, linked from an App Store listing. Section 4 is the part that
matters; everything else is plumbing.

Languages, always: `en de fr es it pt ja ko el uk ru`. The kit uses those codes;
fastlane uses locale directories (`de-DE`, `es-ES`, `fr-FR`, `pt-BR`, and bare
`it ja ko el uk ru`). The kit maps between them — do not invent a mapping.

---

Related: **`appstore-prep`** covers the rest of a submission — the fastlane
lanes, the screenshot set and `docs/RELEASE.md`. The site comes first, because
the listing's support and privacy URLs have to resolve before a build can be
submitted.

## 1. Check the ground before asking anything

```sh
ls fastlane/metadata/en-US/            # subtitle.txt and description.txt must exist
find . -name "AppIcon.png" -o -name "*.appiconset" | head
ls fastlane/screenshots/en-US/ 2>/dev/null | head
git remote -v && git status --short
```

**Blockers, and say so rather than working around them:**

- No `fastlane/metadata/en-US/subtitle.txt` + `description.txt` → the landing
  page has no headline or lead. The site reads them from the listing on purpose;
  writing site-only copy instead guarantees the two drift. Stop and say this.
- No 1024×1024 app icon → no `icon-512.png`, and `make_site_card.py` fails.
- No screenshots → the hero has nothing to show. `make shots` first if the app
  has that target.

## 2. Ask, in one round

Use AskUserQuestion. Get these; do not guess:

1. **Slug** for the URL (`ikunin.github.io/apps/<slug>/`). Lowercase, usually
   the app name. Confirm rather than assume.
2. **Publish now, or build only?** Publishing puts the site on the open web
   before the app may be on the store. It is what the other apps do, but it is
   outward-facing and irreversible-ish, so ask.
3. Anything the *facts* below cannot be read from the repo.

**Read, do not ask, when the repo can answer:**

| Fact | Where |
|---|---|
| Palette | the app's theme/palette source — take the real hex values |
| Family Shareable? | `*.storekit` → `familyShareable` |
| What is sold | `*.storekit` product names, and the app's paywall |
| Declared APIs | `PrivacyInfo.xcprivacy` — quote the reasons verbatim |
| What is stored | the app's persistence layer / record type |
| Impressum, support email | another app's `appstore/site_config.py` |

## 3. Install the kit

```sh
git submodule add https://github.com/ikunin/appsite.git vendor/appsite
mkdir -p appstore && cp vendor/appsite/template/*.py appstore/
```

The template holds every script the recipe runs. If one is missing, the
submodule is old — `git submodule update --remote vendor/appsite`.

Then `appstore/site_config.py`: brand, `PAGES`, `theme_color`, `palette` from the
app's own theme, `impressum` copied from a sibling app, `store=""` until live.

**Already has a site?** This is safe to re-run: `make site` regenerates every
page from the config and the text tables. Rebuild, `git diff`, and expect
nothing but what you changed — that is also the kit's own gate after a change to
`vendor/appsite`.

## 4. Rewrite the legal text — the actual work

`appstore/site_text_privacy.py`, `_support.py`, `_terms.py` each carry eleven
languages of another app's words. Rewrite the app-specific keys in **all
eleven**, then replace every remaining mention of the other app's name.

Check each of these against the source, and expect at least one to be false:

| Key | Checked against | Was wrong for MorseHero |
|---|---|---|
| `p_family` | `*.storekit` `familyShareable` | template claimed Family Shareable; it is not |
| `p_content` | what the app actually imports | template said MIDI files; app takes pasted text |
| `p_music` | what ships in the bundle | template licensed a soundfont; app synthesises its tone |
| `p_api` | `PrivacyInfo.xcprivacy` | must be the real declarations, verbatim |
| `p_children` | the age rating | template said "designed for children" |
| `list` | the app's own stored record | |
| `p_purchases`, `p_pro` | the storekit products | |
| `note` | the privacy manifest's collected-data array | add anything the template had no reason to mention — a microphone, a camera |

The **support FAQ is not translatable filler**. Throw the template's questions
away and write the ones this app is actually asked. The valuable ones are where
the honest answer is counter-intuitive and the app otherwise looks broken.

Practical method — it survives typos and keeps the diff reviewable:

```python
# per language: only the keys that change, merged over the template
merged = dict(template[lang]); merged.update(mine[lang])
# then, everything the template still says about the other app
merged = {k: v.replace("OtherApp", "ThisApp") for ...}
```
Write the result with `pprint.pformat(out, width=100, sort_dicts=False)` and a
header naming which keys were rewritten and why. Assert the language sets and
key sets match before writing — a missing language fails at render time, a
missing key fails silently as the other app's sentence.

## 5. The landing page

`appstore/make_site_translations.py` holds `T` (eleven languages of section copy)
and `page()` (the blocks). The template ships **English only**, so the first
`make site` stops with `no landing copy for: de, fr, …` — that is the
instruction, not a fault. The hero's headline and lead are read from the
listing; leave that alone. Replace the sections with this app's, and the
`img(...)` names and alt text with this app's screenshots.

A macOS app says so in `eyebrow` and `lockup` (`iPhone, iPad and Apple silicon
Mac`), and its shots are landscape rather than 440×956.

Keep it to four or five sections. Cards are `(title, body)` tuples. `blocks.stats`
zeros are a claim the privacy manifest has to back.

## 6. Assets

```sh
mkdir -p site/img
python3 - <<'PY'
from PIL import Image
src = Image.open("<path to 1024 AppIcon.png>").convert("RGB")
for name, size in (("icon-512.png", 512), ("apple-touch-icon.png", 180),
                   ("favicon-32.png", 32)):
    src.resize((size, size), Image.LANCZOS).save(f"site/img/{name}")
# Landing shots: portrait, 440×956, three across.
for src_name, dst in (("1-...", "a.png"), ("4-...", "b.png"), ("7-...", "c.png")):
    Image.open(f"fastlane/screenshots/en-US/{src_name}.png").convert("RGB") \
        .resize((440, 956), Image.LANCZOS).save(f"site/img/{dst}")
PY
```

## 7. Translate the App Store listing

The site's headline and lead come from here, so the other ten locales are not
optional. Per locale: `subtitle keywords promotional_text release_notes
description name marketing_url support_url privacy_url`.

**Hard limits, and Connect rejects rather than truncates.** `check_site.py`
measures every field in every locale, so `make site` catches an overrun before a
submission does — but knowing them while writing saves a round trip:

| Field | Limit |
|---|---|
| `name`, `subtitle` | 30 characters |
| `keywords` | 100 characters |
| `promotional_text` | 170 characters |
| `description`, `release_notes` | 4000 characters |

A translation is longer than its source more often than not, so the English one
fitting says nothing about the other ten.

`copyright.txt` and `primary_category.txt` live at the **metadata root**, not per
locale. Move them if a previous setup put them in `en-US/`.

The URLs point at the site, in every locale:

```
https://ikunin.github.io/apps/<slug>/
https://ikunin.github.io/apps/<slug>/support.html
https://ikunin.github.io/apps/<slug>/privacy.html
```

**zsh does not word-split unquoted variables.** `for l in $LOCALES` makes one
directory named after all ten. Write the list literally, or use python.

## 8. Wire it up and check

Add to the Makefile (`.PHONY` too), in this order — `install_site_assets` first,
`check_site` last:

```make
site:
	python3 appstore/install_site_assets.py
	python3 appstore/make_site_translations.py
	python3 appstore/make_site_legal.py
	python3 appstore/make_site_impressum.py
	python3 appstore/make_site_card.py
	python3 appstore/check_site.py
```

`make site` must end in `all tests passed`: every internal link resolves, every
image has alt text, and every locale's listing URLs resolve to a page that
exists. A `FAIL ... does not exist` naming another app's image means section 5
was skipped.

Add `__pycache__/` to `.gitignore` before staging.

## 9. Commit, then publish

Commit the site with the app (`site/` is tracked, as in every sibling app). Then:

```sh
python3 vendor/appsite/publish.py --app <slug> --site site --dry-run
```

Read the dry run. It must touch **only** `<slug>/` plus the root `index.html`
and `impressum.html`. Anything else means stop.

```sh
python3 vendor/appsite/publish.py --app <slug> --site site
```

The root index is rebuilt from every `app.json` on the branch — the app is
listed because it published, so there is nothing to edit to add it. If only the
index's own wording changes, `--index-only` rebuilds that and nothing else.

Verify, and expect the index to lag: the app's own pages are live at once, the
rebuilt index takes ~20 s through GitHub Pages' cache. Poll rather than
concluding it failed.

```sh
curl -sfo /dev/null -w '%{http_code} %{url_effective}\n' \
  https://ikunin.github.io/apps/<slug>/ \
  https://ikunin.github.io/apps/<slug>/privacy.html \
  https://ikunin.github.io/apps/<slug>/ja/index.html
curl -s https://ikunin.github.io/apps/ | grep -c '<slug>/'
```

## 10. If you changed the kit

Anything fixed in `vendor/appsite` belongs upstream, or the next app hits it too:

```sh
cd vendor/appsite && python3 tests/test_appsite.py     # its own tests
```

Then rebuild a shipped app's site and expect **no diff** — that is the kit's
gate, and it is coarser and more honest than the unit tests. Push the kit, then
bump the submodule pointer in the app.

## 11. Write it down

`docs/RELEASE.md`: how to build and publish, that the legal text is this app's
own promise and where it lives, and the subtitle character cap. Then commit and
push.

---

## Report honestly

Say which template statements were false and what they were replaced with — that
is the part with consequences. Say the site is publicly reachable before the app
is on the store, and offer to pull it if that is not wanted. Name what is still
manual.
