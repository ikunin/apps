#!/usr/bin/env python3
"""Copy an app's built site onto the gh-pages branch of this repository.

One GitHub Pages site serves every app, one directory each:

    ikunin.github.io/apps/tappymusic/
    ikunin.github.io/apps/harborrush/
    ikunin.github.io/apps/speedycards/

`main` stays the kit — code, template, tests. `gh-pages` holds only generated
output. Keeping them apart matters for the same reason the kit exists: a
generated copy sitting next to its own source is the thing that drifts, and
nobody notices until the published page and the repository disagree.

Run from an app's repository, after `make site`:

    python3 vendor/appsite/publish.py --app harborrush --site site

It clones gh-pages into a temporary directory, replaces that one app's
subdirectory, commits and pushes. Nothing else on the branch is touched, so
publishing one app cannot remove another.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

REMOTE = "https://github.com/ikunin/apps.git"
BRANCH = "gh-pages"


def run(*command, cwd=None, check=True):
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if check and result.returncode != 0:
        sys.exit(f"{' '.join(command)}\n{result.stdout}{result.stderr}")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", required=True,
                        help="directory on the branch, e.g. harborrush")
    parser.add_argument("--site", default="site", help="built site to publish")
    parser.add_argument("--remote", default=REMOTE)
    parser.add_argument("--message", default=None)
    parser.add_argument("--dry-run", action="store_true",
                        help="prepare and report, but do not push")
    args = parser.parse_args()

    if not os.path.isdir(args.site):
        sys.exit(f"{args.site}: not there — run `make site` first")
    pages = [name for _, _, names in os.walk(args.site)
             for name in names if name.endswith(".html")]
    if not pages:
        sys.exit(f"{args.site}: no pages in it, refusing to publish an empty site")

    with tempfile.TemporaryDirectory() as work:
        checkout = os.path.join(work, "pages")
        cloned = run("git", "clone", "--depth", "1", "--branch", BRANCH,
                     args.remote, checkout, check=False)
        if cloned.returncode != 0:
            # First publish: an orphan branch, so gh-pages carries none of the
            # kit's history.
            run("git", "clone", "--depth", "1", args.remote, checkout)
            run("git", "checkout", "--orphan", BRANCH, cwd=checkout)
            run("git", "rm", "-rqf", "--ignore-unmatch", ".", cwd=checkout)
            with open(os.path.join(checkout, ".nojekyll"), "w") as handle:
                handle.write("")   # serve _-prefixed paths and skip Jekyll
            with open(os.path.join(checkout, "index.html"), "w") as handle:
                handle.write(INDEX)

        target = os.path.join(checkout, args.app)
        shutil.rmtree(target, ignore_errors=True)
        shutil.copytree(args.site, target)

        run("git", "add", "-A", cwd=checkout)
        status = run("git", "status", "--short", cwd=checkout).stdout.strip()
        if not status:
            print(f"{args.app}: already published, nothing changed")
            return
        if args.dry_run:
            print(f"{args.app}: would publish {len(pages)} pages\n{status[:600]}")
            return

        run("git", "-c", "user.email=kunin.igor@gmail.com", "-c", "user.name=ikunin",
            "commit", "-q", "-m",
            args.message or f"Publish {args.app}: {len(pages)} pages", cwd=checkout)
        run("git", "push", "-q", "origin", BRANCH, cwd=checkout)
        print(f"{args.app}: published {len(pages)} pages to {BRANCH}")


INDEX = """<!doctype html>
<meta charset="utf-8">
<title>Apps</title>
<meta name="robots" content="noindex">
<p>Nothing here. Each app has its own directory.</p>
"""


if __name__ == "__main__":
    main()
