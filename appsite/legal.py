"""Support, privacy and terms: the three pages every app on the store needs.

The *structure* is here and is shared. The *words* are not, and deliberately
so — a sentence in a privacy policy that has to change for one app must not
change for the others. `appsite.boilerplate` is a starting point an app copies
once and then owns.

A page is a flat list of blocks, so the three pages differ only in the blocks
they list. An app whose terms need a section about its soundfont adds one; an
app whose terms do not, does not.
"""

import html

from .languages import LANGUAGES, ORIGINAL_LINK_LABEL

#: Links every app's terms and privacy pages need, so nobody retypes them.
APPLE_EULA = ("https://www.apple.com/legal/internet-services/itunes/dev/"
              "stdeula/")
APPLE_REFUNDS = "https://reportaproblem.apple.com"
GITHUB_PRIVACY = ("https://docs.github.com/site-policy/privacy-policies/"
                  "github-general-privacy-statement")


def link(href, text):
    return f'<a href="{href}">{text}</a>'


# --------------------------------------------------------------- blocks ---
# Every block takes markup, not text: escaping is the caller's decision,
# because most of this prose carries <strong>, <code> and links.

def p(markup):
    return ("p", markup)


def muted(markup):
    return ("muted", markup)


def note(markup):
    return ("note", markup)


def heading(text):
    return ("h3", html.escape(text))


def bullets(items):
    return ("ul", [html.escape(item) for item in items])


def faq(pairs):
    """Question and answer pairs. Questions are text, answers are markup."""
    return ("dl", pairs)


_RENDER = {
    "p": lambda v: f"  <p>{v}</p>\n",
    "muted": lambda v: f'  <p class="muted">{v}</p>\n',
    "note": lambda v: f'  <div class="note"><p>{v}</p></div>\n',
    "h3": lambda v: f"  <h3>{v}</h3>\n",
    "ul": lambda v: "  <ul>\n" + "".join(f"    <li>{i}</li>\n" for i in v) + "  </ul>\n",
    "dl": lambda v: '  <dl class="faq">\n' + "".join(
        f"    <dt>{html.escape(q)}</dt>\n    <dd>{a}</dd>\n\n" for q, a in v
    ) + "  </dl>\n",
}

#: Blocks that open a new thought, and get a blank line above them.
_BREAK_BEFORE = {"h3", "note", "dl"}
#: Blocks after which a blank line reads better — a dateline is not part of
#: the paragraph that follows it.
_BREAK_AFTER = {"muted"}


def render(blocks):
    out = []
    previous = None
    for kind, value in blocks:
        if out and (kind in _BREAK_BEFORE or previous in _BREAK_AFTER):
            out.append("\n")
        out.append(_RENDER[kind](value))
        previous = kind
    return "".join(out)


# ---------------------------------------------------------------- page ---

def governing(language, name):
    """The line saying which version wins. Nothing on the original."""
    clause = LANGUAGES[language].governing
    if not clause:
        return []
    original = link(f"../{name}", ORIGINAL_LINK_LABEL)
    return [muted(clause.format(link=original))]


def page(site, language, name, *, title, description, headline, blocks,
         say_which_version_governs=True):
    """One legal page, in one language.

    `say_which_version_governs` exists for pages where it would be nonsense —
    a support page makes no promises — not as a way to leave it off a policy.
    """
    if say_which_version_governs:
        blocks = list(blocks) + governing(language, name)
    body = render(blocks)
    main = (
        '<main class="legal"><div class="wrap">\n\n'
        f"<section>\n  <h2>{html.escape(headline)}</h2>\n"
        f"{body}</section>\n\n"
        "</div></main>\n"
    )
    return site.document(language, name, title=title, description=description,
                         main=main)
