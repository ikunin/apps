#!/usr/bin/env python3
"""Write this app's card for the portfolio at the root of the Pages site.

site/app.json says what the index at ikunin.github.io/apps/ should show for this
app: its name, the App Store subtitle it already ships, its icon and its accent.
Publishing copies site/ wholesale, so the card rides up with the pages and the
index is rebuilt from it.

Nothing here is written twice. Every field is read from site_config.py or from
the App Store metadata, and a card that would be wrong — no icon on disk, an
empty subtitle — fails this build rather than the publish.

Run it after the pages: it checks that the icon it names is really there.
"""

from site_config import SITE

from appsite import portfolio

if __name__ == "__main__":
    print(f"wrote {portfolio.write(SITE)}")
