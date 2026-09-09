#!/usr/bin/env python3
"""STARTING POINT — the landing page, and the one file here that is entirely
this app's.

Unlike the legal text, there is nothing to inherit: every sentence below the
hero describes a particular program. What the template gives you is the shape —
which blocks exist, how a translated page reaches the images, and where the copy
for eleven languages goes.

**The hero is not written here.** Its headline and opening paragraph are read
from the App Store listing — `fastlane/metadata/<locale>/subtitle.txt` and
`description.txt` — because those words are already translated, already
reviewed, and are what a customer meets before they ever reach the site.
Translating the same pitch twice guarantees the two drift apart.

`T` below carries English only. `main()` refuses to build until every language
the site declares has copy, and names the ones missing — that refusal is the
point. Fill them in; do not delete the check.

The stats row is a claim, not decoration. A zero there has to be backed by
`PrivacyInfo.xcprivacy`: print it only if the manifest says so.
"""

import html

from site_config import SITE

from appsite import blocks, listing

LANGUAGES_SPOKEN = 11

T = {
    "en": {
        "eyebrow": "For iPhone and iPad",
        "cta1": "How it works", "cta2": "Support",
        # Four short words under the hero. Two of them are usually zeros.
        "stats": ["languages", "trackers", "ads", "free"],

        "h_one": "What it does",
        "p_one": "One paragraph on the thing this app does that the others do not. "
                 "Not a feature list — the reason it exists.",
        "c_one": [
            ("A short title", "Two sentences. The second earns the first."),
            ("Another", "Cards are (title, body) tuples and are escaped for you."),
            ("A third", "Three reads better than two or four."),
        ],

        "h_two": "And the consequence of it",
        "p_two": "The second section is usually what the first one costs or buys.",
        "p_free": "<strong>What is free, stated plainly.</strong> Then what one "
                  "purchase unlocks, and that it does not renew.",

        "h_three": "How it is used",
        "c_three": [
            ("One way", "…"),
            ("Another way", "…"),
            ("A third way", "…"),
        ],

        "h_privacy": "Nothing leaves the phone",
        "p_note": "<strong>No account. No analytics. No network.</strong> Say only "
                  "what the privacy manifest backs. The "
                  "<a href='privacy.html'>privacy policy</a> says exactly what "
                  "stays where.",
        "p_langs": "The app speaks eleven languages: English, German, French, "
                   "Spanish, Italian, Brazilian Portuguese, Japanese, Korean, "
                   "Greek, Ukrainian and Russian.",
        "cta_privacy": "Read the privacy policy", "cta_support": "Get support",
        "lockup": "Free to try, unlocked with one purchase. iPhone and iPad, "
                  "eleven languages, nothing uploaded.",

        # Alt text is not optional: check_site.py fails a build without it, and
        # it is the only description a screen reader gets of a screenshot.
        "alt_one": "…", "alt_two": "…", "alt_three": "…",
    },
}


def page(language):
    s = T[language]
    line1, line2 = listing.headline(SITE, language)
    lead = listing.lead(SITE, language)

    # Images live once, at the site root; a translated page reaches up for them.
    root = "" if language == "en" else "../"

    def img(name):
        return f"{root}img/{name}"

    def card_list(key):
        return blocks.cards([(html.escape(title), html.escape(body))
                             for title, body in s[key]])

    hero = blocks.hero(
        eyebrow=html.escape(s["eyebrow"]),
        headline=(
            f'{html.escape(line1)}<br><span class="glow">{html.escape(line2)}</span>'
            if line1 else f'<span class="glow">{html.escape(line2)}</span>'
        ),
        lead=html.escape(lead),
        buttons=blocks.actions([
            blocks.button(s["cta1"], "#how"),
            blocks.button(s["cta2"], SITE.local(language, "support.html"), ghost=True),
        ]),
        parts=[
            # Portrait captures at 440×956, so three sit across rather than
            # three letterboxes. Export them into site/img/ yourself.
            blocks.shots([
                (img("one.png"), s["alt_one"], 440, 956, "eager"),
                (img("two.png"), s["alt_two"], 440, 956, "lazy"),
                (img("three.png"), s["alt_three"], 440, 956, "lazy"),
            ]),
            blocks.stats([
                (LANGUAGES_SPOKEN, s["stats"][0]),
                (0, s["stats"][1]),
                (0, s["stats"][2]),
                ("—", s["stats"][3]),
            ]),
        ],
    )

    sections = [
        blocks.section(s["h_one"], [
            blocks.paragraph(html.escape(s["p_one"])),
            card_list("c_one"),
        ], anchor="how"),

        blocks.section(s["h_two"], [
            blocks.paragraph(html.escape(s["p_two"])),
            blocks.paragraph(s["p_free"]),
        ]),

        blocks.section(s["h_three"], [card_list("c_three")]),

        blocks.section(s["h_privacy"], [
            blocks.note(s["p_note"]),
            blocks.paragraph(html.escape(s["p_langs"])),
            blocks.actions([
                blocks.button(s["cta_privacy"], SITE.local(language, "privacy.html")),
                blocks.button(s["cta_support"], SITE.local(language, "support.html"),
                              ghost=True),
            ], style="justify-content: flex-start;"),
            "\n",
            blocks.lockup(icon=img("icon-512.png"),
                          heading=SITE.chrome.brand.replace("&nbsp;", " "),
                          text=s["lockup"]),
        ]),
    ]

    return SITE.document(
        language, "index.html",
        title=f"{SITE.chrome.brand.replace('&nbsp;', ' ')} — "
              f"{html.escape((line1 + ' ' + line2).strip())}",
        description=html.escape(lead[:180]),
        main=blocks.landing(hero, sections),
    )


def main():
    missing = [code for code in SITE.languages if code not in T]
    if missing:
        raise SystemExit("no landing copy for: " + ", ".join(missing))
    for language in SITE.languages:
        SITE.write(language, "index.html", page(language))
    print(f"wrote {len(SITE.languages)} landing pages")


if __name__ == "__main__":
    main()
