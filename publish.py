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

The root index is then rebuilt from every `app.json` on the branch — see
`appsite/portfolio.py`. It is derived, never edited: an app appears there
because it has published, and a fourth app needs no change here.

    python3 vendor/appsite/publish.py --index-only

rebuilds only that root, for when its own wording changes.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from appsite import portfolio  # noqa: E402

REMOTE = "https://github.com/ikunin/apps.git"
BRANCH = "gh-pages"


def run(*command, cwd=None, check=True):
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if check and result.returncode != 0:
        sys.exit(f"{' '.join(command)}\n{result.stdout}{result.stderr}")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", default=None,
                        help="directory on the branch, e.g. harborrush")
    parser.add_argument("--site", default="site", help="built site to publish")
    parser.add_argument("--index-only", action="store_true",
                        help="rebuild the root index, publishing no app")
    parser.add_argument("--remote", default=REMOTE)
    parser.add_argument("--message", default=None)
    parser.add_argument("--dry-run", action="store_true",
                        help="prepare and report, but do not push")
    args = parser.parse_args()

    if bool(args.app) == bool(args.index_only):
        sys.exit("say either --app <name> or --index-only")

    pages = []
    if args.app:
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

        if args.app:
            target = os.path.join(checkout, args.app)
            shutil.rmtree(target, ignore_errors=True)
            shutil.copytree(args.site, target)

        # The root is derived from what is on the branch, so it is rebuilt on
        # every publish and never edited. An app is on it because it published.
        apps = portfolio.build(checkout)
        problems = portfolio.check_root(checkout)
        for problem in problems:
            print(f"  FAIL {problem}")
        if problems:
            sys.exit(f"the index has {len(problems)} problems, not publishing")
        listed = ", ".join(slug for slug, _ in apps)
        count = f"{len(apps)} app" + ("" if len(apps) == 1 else "s")
        what = f"Publish {args.app}: {len(pages)} pages" if args.app \
            else f"Rebuild the index: {count}"

        run("git", "add", "-A", cwd=checkout)
        status = run("git", "status", "--short", cwd=checkout).stdout.strip()
        if not status:
            print(f"{args.app or 'index'}: already published, nothing changed")
            return
        print(f"index: {count} — {listed}")
        if args.dry_run:
            print(f"would commit: {what}\n{status[:600]}")
            return

        run("git", "-c", "user.email=kunin.igor@gmail.com", "-c", "user.name=ikunin",
            "commit", "-q", "-m", args.message or what, cwd=checkout)
        run("git", "push", "-q", "origin", BRANCH, cwd=checkout)
        print(f"{what} — pushed to {BRANCH}")


if __name__ == "__main__":
    main()
