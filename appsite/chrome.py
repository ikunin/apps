"""Header, footer, language switcher and hreflang links.

One implementation, called by every page of every kind. Two copies of a
navigation is exactly how a German page ends up with an English menu after
somebody renames a link — it had already happened once before this was
extracted.
"""

import html
from dataclasses import dataclass, field

from .languages import LANGUAGES


@dataclass(frozen=True)
class Page:
    """A page in the navigation.

    - `kind` looks the label up in `Language.nav`; a kind the kit does not know
      needs `labels`, which is how an app adds a page of its own (a song list,
      a level guide) without that label leaking into the kit.
    - `translated` says whether the page exists per language. A page that is
      not translated lives at the root and every translated page links up to
      it — the song list, whose content is proper nouns, or the Impressum,
      which German law wants in German.
    """

    kind: str
    file: str
    translated: bool = True
    labels: dict = field(default_factory=dict)   # language code -> label

    def label(self, language):
        if self.labels:
            return self.labels[language]
        return LANGUAGES[language].nav[self.kind]


@dataclass(frozen=True)
class Chrome:
    """Everything that wraps a page and is identical across pages.

    `brand` is markup, not text: it usually wants a non-breaking space so the
    app's name cannot wrap in the header.
    """

    brand: str
    icon: str
    pages: tuple
    copyright: str
    icon_size: int = 512

    def language_codes(self):
        return list(LANGUAGES)

    def render(self, language, current):
        """Returns (header, footer, alternates, root) for one page.

        `current` is the page's file name: it marks the right nav item, and it
        decides the depth every other link is written relative to.
        """
        root = "" if language == "en" else "../"
        translated = {page.file for page in self.pages if page.translated}

        def href(code):
            """Where this page's sibling lives in another language."""
            if code == "en":
                return ("./" if current == "index.html" else current) \
                    if language == "en" \
                    else ("../" if current == "index.html" else f"../{current}")
            prefix = f"{code}/" if language == "en" else f"../{code}/"
            return prefix if current == "index.html" else prefix + current

        def link(page):
            # Pages that are translated sit beside this one; the rest live at
            # the root in their own language, one directory up.
            if language != "en" and page.file not in translated:
                target = f"../{page.file}"
            else:
                target = "./" if page.file == "index.html" else page.file
            mark = ' aria-current="page"' if page.file == current else ""
            return f'      <a href="{target}"{mark}>{html.escape(page.label(language))}</a>\n'

        header = (
            '<header class="site">\n  <div class="wrap">\n'
            f'    <a class="brand" href="./">'
            f'<img src="{root}{self.icon}" alt="" '
            f'width="{self.icon_size}" height="{self.icon_size}">'
            f'{self.brand}</a>\n    <nav class="site">\n'
            + "".join(link(page) for page in self.pages)
            + '    </nav>\n  </div>\n</header>\n'
        )

        # A page that exists in only one language has nothing to switch to and
        # no alternates to declare. It gets an ordinary footer nav instead —
        # every page but itself, which is what a reader at the bottom of it
        # wants.
        if current not in translated:
            links = "".join(
                f'      <a href="{page.file if page.file != "index.html" else "./"}">'
                f"{html.escape(page.label(language))}</a>\n"
                for page in self.pages if page.file != current
            )
            footer = ('<footer class="site">\n  <div class="wrap">\n'
                      f'    <span>{self.copyright}</span>\n'
                      f"    <nav>\n{links}    </nav>\n"
                      '  </div>\n</footer>\n')
            return header, footer, "", root

        switcher = "".join(
            f'<a href="{href(code)}" hreflang="{code}" lang="{code}"'
            f'{" aria-current=\"page\"" if code == language else ""}>'
            f'{html.escape(LANGUAGES[code].name)}</a>'
            for code in self.language_codes()
        )
        footer = (
            '<footer class="site">\n  <div class="wrap">\n'
            f'    <span>{self.copyright}</span>\n'
            f'    <nav class="languages">{switcher}</nav>\n'
            '  </div>\n</footer>\n'
        )

        alternates = "\n".join(
            f'<link rel="alternate" hreflang="{code}" href="{href(code)}">'
            for code in self.language_codes()
        ) + f'\n<link rel="alternate" hreflang="x-default" href="{href("en")}">'

        return header, footer, alternates, root
