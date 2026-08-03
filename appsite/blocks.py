"""The landing page, as a vocabulary rather than a template.

A landing page is where two apps differ most, so this is deliberately not one
fixed shape with holes in it. It is the set of pieces the stylesheet knows how
to draw — hero, cards, showcase, note, lockup, stats — and each app composes
the ones it needs, in the order it needs them.

Every function returns markup. Text that comes from an app's copy is escaped
by the caller where it is plain and passed through where it carries <strong>
or a link, which is the same bargain `legal.py` makes.
"""

import html


def button(label, href, ghost=False):
    kind = "button ghost" if ghost else "button"
    return f'<a class="{kind}" href="{href}">{html.escape(label)}</a>'


def actions(buttons, *, style=""):
    attr = f' style="{style}"' if style else ""
    inner = "".join(f"    {b}\n" for b in buttons)
    return f'  <div class="actions"{attr}>\n{inner}  </div>\n'


def shots(images, *, wide=False):
    """The screenshots under the hero. Each: (src, alt, w, h, loading).

    Portrait shots are fanned, which reads as a phone. `wide=True` lays
    landscape shots out as a grid instead — three fanned letterboxes are a
    stack of slivers with nothing visible in them.
    """
    figures = "".join(
        f'    <figure><img src="{src}" alt="{html.escape(alt)}" '
        f'width="{w}" height="{h}" loading="{loading}"></figure>\n'
        for src, alt, w, h, loading in images
    )
    kind = "shots wide" if wide else "shots"
    return f'  <div class="{kind}">\n{figures}  </div>\n'


def stats(pairs):
    """Big numbers. Each: (value, label). A zero is worth showing — "0 trackers"
    is a claim, and the stylesheet gives it the same weight as the rest."""
    rows = "".join(
        f"    <div><b>{value}</b><span>{html.escape(label)}</span></div>\n"
        for value, label in pairs
    )
    return f'  <div class="stats">\n{rows}  </div>\n'


def hero(*, headline, lead, eyebrow=None, emblem=None, buttons=None, parts=()):
    """The top of the page.

    `headline` is markup — it usually carries a <span class="glow"> on the half
    of the line that should catch light. `buttons` sits directly under the
    lead; each of `parts` is separated from what precedes it by a blank line,
    because they are separate objects on the page rather than one block of
    text.
    """
    out = ['<div class="hero wrap">\n']
    if emblem:
        src, w, h = emblem
        out.append('  <div class="emblem">\n'
                   f'    <img src="{src}" alt="" width="{w}" height="{h}" '
                   'loading="eager">\n  </div>\n')
    if eyebrow:
        out.append(f'  <p class="eyebrow">{html.escape(eyebrow)}</p>\n')
    out.append(f"  <h1>{headline}</h1>\n")
    out.append(f'  <p class="lead">{html.escape(lead)}</p>\n')
    if buttons:
        out.append(buttons)
    for part in parts:
        out.append("\n" + part)
    out.append("</div>\n")
    return "".join(out)


def cards(entries):
    """Three-across feature cards. Each: (title, body); title may be markup."""
    inner = "".join(
        f'    <div class="card">\n      <h3>{title}</h3>\n'
        f"      <p>{body}</p>\n    </div>\n"
        for title, body in entries
    )
    return f'  <div class="cards">\n{inner}  </div>\n'


def showcase(*, image, heading, paragraphs):
    """A screenshot beside prose. `image` is (src, alt, w, h)."""
    src, alt, w, h = image
    body = "".join(f"      {para}\n" for para in paragraphs)
    return ('  <div class="showcase">\n'
            f'    <img src="{src}" alt="{html.escape(alt)}" '
            f'width="{w}" height="{h}" loading="lazy">\n'
            f"    <div>\n      <h3>{html.escape(heading)}</h3>\n{body}    </div>\n"
            "  </div>\n")


def note(markup):
    return f'  <div class="note"><p>{markup}</p></div>\n'


def lockup(*, icon, heading, text, size=512):
    """The app, restated at the foot of the page for anyone who scrolled past
    the hero without reading it."""
    return ('  <div class="lockup">\n'
            f'    <img src="{icon}" alt="" width="{size}" height="{size}">\n'
            f"    <div>\n      <h3>{html.escape(heading)}</h3>\n"
            f"      <p>{html.escape(text)}</p>\n    </div>\n  </div>\n")


def paragraph(markup):
    return f"  <p>{markup}</p>\n"


def section(heading, parts, *, anchor=None):
    attr = f' id="{anchor}"' if anchor else ""
    return (f"<section{attr}>\n  <h2>{html.escape(heading)}</h2>\n"
            + "".join(parts) + "</section>\n")


def landing(hero_markup, sections):
    """<main> for a landing page: the hero at full bleed, the rest in a wrap."""
    body = "\n".join(sections)
    return f"<main>\n\n{hero_markup}\n<div class=\"wrap\">\n\n{body}\n</div>\n</main>\n"
