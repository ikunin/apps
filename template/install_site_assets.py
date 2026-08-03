#!/usr/bin/env python3
"""Copy the kit's stylesheet into site/.

site/style.css is generated, like every other page here. The source is
vendor/appsite/appsite/assets/style.css; edit that, not the copy.
"""

from site_config import SITE

from appsite import assets

if __name__ == "__main__":
    print(f"wrote {assets.install(SITE)}")
