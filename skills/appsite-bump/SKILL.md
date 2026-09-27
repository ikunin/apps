---
name: appsite-bump
description: 'Move every app repository''s vendor/appsite submodule up to the kit''s current commit, rebuild each site, check the byte-identical gate, commit, push, and publish only what actually changed. Use when the user says "/appsite-bump", "bump the submodules", "update the submodule pointers", "follow the kit", or after landing a change in the appsite kit that the apps should pick up.'
---

A kit change is not a site change until each app's submodule pointer moves and
its `make site` runs. This is that pass. It is mostly reading diffs; the one
thing it must never do is commit a rebuild nobody looked at.

## 0. Survey before touching anything

```sh
python3 ~/.claude/skills/appsite-bump/survey.py       # read-only
```

It finds every repository holding `vendor/appsite`, and prints each one's pin,
how far behind the kit it is, its branch, and whether its tree is dirty.

**Then call `ListAgents`.** A repository is off limits while another session is
busy in it — a bump rewrites `site/` under that session's feet. Skip it, say so
by name, and offer to come back.

Skip a repository, do not "fix" it, when:

- tracked files are modified — somebody's work in progress, and `git add
  vendor/appsite` next to it invites staging theirs by accident;
- it is not on `main` — a feature branch bumps when it lands, not before;
- a session in `ListAgents` is busy or in a shell there.

## 1. The kit's commit has to be pushed first

Pin to a commit on the kit's `origin/main`. A pin at a local-only commit is a
repository nobody else can clone.

```sh
git -C <kit> log --oneline -1 origin/main
```

## 2. Per repository: bump, rebuild, read

```sh
cd <app>
git -C vendor/appsite fetch -q origin && git -C vendor/appsite checkout -q <sha>
make site                      # runs the app's own check_site.py at the end
git diff --stat -- site
```

**A vendored file edited in place blocks the checkout.** Save it before
discarding it — and note what it was: an edit inside `vendor/appsite` is a
change made to the copy instead of to the kit, so its content usually belongs
in the kit.

```sh
git -C vendor/appsite diff > /tmp/<app>-vendored.patch
git -C vendor/appsite checkout -- .
```

## 3. The gate

**Byte-identical is the expected result.** Kit work is mostly guards,
resolvers and documentation; a bump that re-renders nothing is the bump
working. So:

- **no diff** → the pointer is the whole commit, and nothing needs publishing;
- **a diff** → read every hunk and be able to say which kit commit produced it
  before committing. A diff you cannot attribute is a regression, not a bump.

`site/app.json` is the one file that moves on its own: it is the card the root
index is built from, and a field leaves it when the index stops reading it.

## 4. Commit, push, publish only what moved

Stage by name — `vendor/appsite` plus whatever under `site/` the rebuild wrote.
Never `git add -A`: these trees carry other people's work.

The message names what came up with the kit and states the gate's result, so a
later reader knows whether the bump was output-neutral without rebuilding it.

```sh
git push origin main
python3 vendor/appsite/publish.py --app <slug> --site site    # ONLY if site/ changed
```

Publishing rebuilds the root index from every card on the branch, so a publish
is never local to one app. Afterwards, confirm the branch rather than the
page — GitHub's CDN serves the old copy for a few minutes:

```sh
git -C <kit> fetch -q origin gh-pages
git -C <kit> diff --stat <before> origin/gh-pages
```

The apps' `localci` hook runs a content job on push, in seconds. It is not the
test suite: for an app whose *code* changed, build and test it yourself.

## 5. Report

Per repository: the pin it came from, the pin it is on, what the gate said,
and whether it was published. Name every repository you skipped and why —
a silent skip is how one app stays a kit behind for months.
