"""Everything `appsite.portfolio` needs to know about THE ROOT of the site.

`site_config.py` is this file's opposite number in each app: the kit holds the
structure, and the config holds the facts and the words. This one belongs to the
root of `ikunin.github.io/apps/` — the page that lists the apps — and it is the
only place its wording, its colours and its § 5 address are written down.

The page deliberately says very little. A card carries an app's own icon, name
and App Store subtitle, and that is all. Anything written *about the apps* would
be a sentence about three different programs at once, and the three differ in
what they collect; AGENTS.md records the time such a sentence was published and
was false. If you want to say more about an app, say it on that app's site.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from appsite import Chrome, Page, Site  # noqa: E402

#: This site is English. Each card leads into an app's own site, which is in
#: eleven languages — so `translated=False` here is the truth, and it is also
#: what keeps a language switcher off a page that has nothing to switch to.
PAGES = (
    Page("home", "index.html", translated=False),
    Page("impressum", "impressum.html", translated=False),
)

SITE = Site(
    chrome=Chrome(
        brand="Igor&nbsp;Kunin",
        icon="favicon.svg",
        icon_size=64,
        pages=PAGES,
        copyright="© Igor Kunin 2026",
    ),
    # `out` is set when the page is built: it is a checkout of gh-pages, in a
    # temporary directory, and only publish.py knows where.
    out=".",
    # One mark, no touch icon. `Site` writes neither <link> when it is empty.
    favicon="favicon.svg",
    favicon_sizes="any",
    apple_touch="",
    languages=("en",),
    # Empty on purpose — see PALETTE_FROM below. The palette is not written
    # here because it is not owned here.
    palette={},
)

#: Whose colours this page wears.
#:
#: A page about three apps has to look like something, and the kit's default
#: palette is TappyMusic's. SpeedyCards' felt-and-brass is the one that reads
#: as a shelf rather than as one of the products, so the root takes it.
#:
#: It is a *name*, not a copy of the tokens: the palette is read from the card
#: SpeedyCards publishes, so restyling that app and republishing it restyles
#: this page too, and the two cannot fall out of step. Set it to "" to go back
#: to the kit's own colours.
#:
#: Note that this makes the root single-theme, as SpeedyCards' own site is —
#: `Site.palette` writes one unconditional `:root` block, which overrides the
#: stylesheet's light theme along with its dark one.
PALETTE_FROM = "speedycards"

#: § 5 DDG, the two fields of it that describe a page rather than a person.
#: The address, telephone number and contact mail are NOT here: they live in
#: each app's `site_config.py` and nowhere else, and this page reads them from
#: the cards the apps publish. A move stays one edit per app repository.
IMPRESSUM = {
    "app": "Igor Kunin",
    "subject": "Website",
}

TITLE = "Apps by Igor Kunin"
DESCRIPTION = ("The apps I publish on the App Store. Each one has its own site, "
               "with support, privacy and terms.")

#: The whole of the page's own copy: one heading, and no lead under it. The
#: apps speak for themselves, one slogan each.
HERO = "Apps"
LEAD = ""

#: The English note on the root's Impressum, which is otherwise German because
#: § 5 DDG is German law. `{support}` becomes a link to each app's support page:
#: this page has none of its own, and "the app" would be three apps here.
IMPRESSUM_NOTE = (
    "<strong>In English:</strong> this page is the provider identification "
    "German law requires of commercial websites (§ 5 DDG). It names who "
    "operates this site and how to reach them. It is in German because the law "
    "is German. For help with a particular app, use its own support page: "
    "{support}."
)
