#!/usr/bin/env python3
"""Check the published site holds together.

The App Store listing links to a privacy page and a support page, and App
Review follows the privacy link. A page that 404s there is a rejection, so this
runs in `make check` and again in the Pages workflow before deploying.

The checks themselves live in `appsite.check`, so the same failure that would
be caught here is caught for every app.
"""

from site_config import REQUIRED_PAGES, SITE

from appsite import check

if __name__ == "__main__":
    check.main(SITE, required=REQUIRED_PAGES)
