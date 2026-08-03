#!/usr/bin/env python3
"""Generate support, privacy and terms — the same three pages in 11 languages.

The page structure comes from `appsite.legal`; the words come from
site_text_{support,privacy,terms}.py, one dict per language including English.

Unlike the landing page, none of this text comes from the App Store listing:
these pages say what the app does and what you agree to, and there is nowhere
else that says it. The English version governs, and every translated privacy
and terms page says so and links back to it.

Run by `make site`.
"""

import html
import sys

from site_config import SITE
from site_text_privacy import PRIVACY
from site_text_support import SUPPORT
from site_text_terms import TERMS

from appsite import LANGUAGES
from appsite.legal import (APPLE_EULA, APPLE_REFUNDS, GITHUB_PRIVACY, bullets,
                           faq, heading, link, muted, note, p, page)

TERMS_MAIL = "mailto:support@example.com?subject=Terms"   # TODO(app)
SOUNDFONT = "https://example.com/"                        # TODO(app)


def render(language, name, text, blocks, governs=True):
    return page(SITE, language, name,
                title=f'{html.escape(text["title"])} — TappyMusic',
                description=html.escape(text["meta"]),
                headline=text["h"], blocks=blocks,
                say_which_version_governs=governs)


def support(language):
    s = SUPPORT[language]
    return render(language, "support.html", s, [
        p(s["intro"]),
        faq(s["faq"]),
        heading(s["h_report"]),
        p(html.escape(s["p_report"])),
        note(html.escape(s["note"])),
    ], governs=False)   # a support page makes no promises to govern


def privacy(language):
    s = PRIVACY[language]
    return render(language, "privacy.html", s, [
        muted(s["updated"]),
        note(s["note"]),
        heading(s["h_device"]),
        p(html.escape(s["p_device"])),
        bullets(s["list"]),
        p(html.escape(s["p_device_after"])),
        heading(s["h_purchases"]),
        p(s["p_purchases"]),
        p(html.escape(s["p_family"])),
        heading(s["h_children"]),
        p(html.escape(s["p_children"])),
        heading(s["h_api"]),
        p(s["p_api"]),
        heading(s["h_site"]),
        p(s["p_site"].format(github=link(GITHUB_PRIVACY,
                                         html.escape(s["github"])))),
        heading(s["h_changes"]),
        p(html.escape(s["p_changes"])),
        heading(s["h_contact"]),
        p(s["p_contact"].format(support=link("support.html",
                                             html.escape(s["support"])))),
    ])


def terms(language):
    s = TERMS[language]
    return render(language, "terms.html", s, [
        muted(s["updated"]),
        p(s["p_eula"].format(eula=link(APPLE_EULA, html.escape(s["eula"])))),
        heading(s["h_purchases"]),
        p(s["p_purchases"]),
        p(s["p_refunds"].format(refund=link(APPLE_REFUNDS,
                                            "reportaproblem.apple.com"))),
        p(s["p_pro"]),
        heading(s["h_content"]),
        p(html.escape(s["p_content"])),
        heading(s["h_music"]),
        p(s["p_music"].format(sf=link(SOUNDFONT, "MuseScore_General"))),
        heading(s["h_notdo"]),
        p(s["p_notdo"].format(privacy=link("privacy.html",
                                           html.escape(s["privacy"])))),
        heading(s["h_warranty"]),
        p(html.escape(s["p_warranty"])),
        heading(s["h_changes"]),
        p(html.escape(s["p_changes"])),
        heading(s["h_contact"]),
        p(link(TERMS_MAIL, "support@example.com")),
    ])


PAGES = {"support.html": support, "privacy.html": privacy, "terms.html": terms}


def main():
    missing = [f"{name}/{code}" for name, table in
               (("support", SUPPORT), ("privacy", PRIVACY), ("terms", TERMS))
               for code in SITE.languages if code not in table]
    if missing:
        raise SystemExit("no text for: " + ", ".join(missing))

    written = 0
    for language in SITE.languages:
        for name, build in PAGES.items():
            SITE.write(language, name, build(language))
            written += 1
    print(f"wrote {written} legal pages")


if __name__ == "__main__":
    main()
