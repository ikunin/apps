#!/usr/bin/env python3
"""Read-only survey of every repository that vendors the appsite kit.

Prints one line per app: its pin, how far behind the kit's origin/main it is,
its branch, and whether its tree is dirty. Touches nothing — the decision of
what to bump, and what to leave alone, belongs to the caller (and to
`ListAgents`, which this cannot see).
"""

import os
import subprocess

#: Where the app repositories sit. One level of directories, each of which may
#: hold `vendor/appsite`; the kit itself is found through any one of them, so
#: nothing here needs a path to it.
ROOT = os.path.expanduser("~/Projects")


def git(*args, cwd):
    out = subprocess.run(("git",) + args, cwd=cwd, text=True, capture_output=True)
    return out.stdout.strip() if out.returncode == 0 else ""


def apps(root):
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        if os.path.isdir(os.path.join(path, "vendor", "appsite")):
            yield name, path


def main():
    found = list(apps(ROOT))
    if not found:
        raise SystemExit(f"no repository under {ROOT} vendors the kit")

    kit = os.path.join(found[0][1], "vendor", "appsite")
    git("fetch", "-q", "origin", cwd=kit)
    head = git("rev-parse", "--short", "origin/main", cwd=kit)
    print(f"kit origin/main: {head}  ({git('log', '-1', '--format=%s', 'origin/main', cwd=kit)})\n")

    for name, path in found:
        sub = os.path.join(path, "vendor", "appsite")
        # Each submodule is its own clone: without this fetch its `origin/main`
        # is whatever it last saw, and the distance below reads as unknown on
        # exactly the repositories that are furthest behind.
        git("fetch", "-q", "origin", cwd=sub)
        pin = git("rev-parse", "--short", "HEAD", cwd=sub)
        behind = git("rev-list", "--count", f"{pin}..origin/main", cwd=sub) or "?"
        branch = git("rev-parse", "--abbrev-ref", "HEAD", cwd=path)
        tracked = [l for l in git("status", "--porcelain", cwd=path).splitlines()
                   if not l.startswith("??")]
        vendored = git("status", "--porcelain", cwd=sub)
        state = []
        if behind not in ("0", "?"):
            state.append(f"{behind} behind")
        if branch != "main":
            state.append(f"on {branch}")
        if tracked:
            state.append(f"{len(tracked)} modified")
        if vendored:
            state.append("vendored copy edited")
        print(f"  {name:<16} {pin}  {', '.join(state) or 'up to date, clean'}")

    print("\nSkip anything modified, off main, or busy in ListAgents.")


if __name__ == "__main__":
    main()
