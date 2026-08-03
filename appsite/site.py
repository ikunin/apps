"""The app's configuration, and the document every page is poured into.

One `Site` per app, built once in that app's `site_config.py`. Everything the
kit needs to know about an app is here; nothing about a particular app is
anywhere else in the kit.
"""

import os
from dataclasses import dataclass, field

from .chrome import Chrome
from .languages import LANGUAGES


@dataclass(frozen=True)
class Site:
    chrome: Chrome
    #: Directory the pages are written to, relative to the app repository root.
    out: str = "site"
    #: Where the App Store listing text lives. fastlane's layout; TappyMusic
    #: mirrors it under Marketing/.
    metadata: str = os.path.join("fastlane", "metadata")
    theme_color: str = "#07060d"
    favicon: str = "img/favicon-32.png"
    apple_touch: str = "img/apple-touch-icon.png"
    stylesheet: str = "style.css"
    #: CSS custom properties to override the kit's defaults — `{"accent":
    #: "#fed508"}`. Empty means the kit's palette, unchanged.
    palette: dict = field(default_factory=dict)
    #: Language codes this site is built in, in switcher order. The default is
    #: every language the kit knows.
    languages: tuple = tuple(LANGUAGES)

    def directory(self, language):
        return self.out if language == "en" else os.path.join(self.out, language)

    def document(self, language, current, *, title, description, main):
        """A complete page. `main` is the whole <main> element."""
        header, footer, alternates, root = self.chrome.render(language, current)
        # A page that exists in one language declares no alternates, and must
        # not leave a blank line in <head> where they would have been.
        alternates = f"{alternates}\n" if alternates else ""
        return f"""<!doctype html>
<html lang="{language}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="color-scheme" content="dark light">
<meta name="theme-color" content="{self.theme_color}">
<link rel="icon" href="{root}{self.favicon}" sizes="32x32">
<link rel="apple-touch-icon" href="{root}{self.apple_touch}">
<link rel="stylesheet" href="{root}{self.stylesheet}">
{alternates}</head>
<body>

{header}
{main}
{footer}
</body>
</html>
"""

    def write(self, language, name, markup):
        directory = self.directory(language)
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, name), "w", encoding="utf-8") as handle:
            handle.write(markup)

    def local(self, language, name):
        """A link from a page in `language` to a sibling page.

        Beside it if that page is translated, at the root if it is not — the
        one place that rule is written down for page bodies, as `Chrome` is for
        the navigation.
        """
        translated = {page.file for page in self.chrome.pages if page.translated}
        if language == "en" or name in translated:
            return name
        return f"../{name}"
