# Maintaining the app sites

**Read [AGENTS.md](AGENTS.md).** It is the maintained copy; this file exists so
that an agent looking for its own filename finds it.

Three things not to guess at, before you touch anything:

- **Never copy a privacy or terms sentence from one app to another.** The apps
  differ in what they collect, and a copied claim is a false statement.
  AGENTS.md has the table, with the source of every cell in it.
- **Run both checkers before publishing** — `check_text.py` and `make site`.
  Between them they have caught four published bugs.
- **A change here is a change to every published site.** The kit's own suite is
  `python3 tests/test_appsite.py`, and the gate it cannot check for you is that
  every app still renders byte-identically: run `make site` in each app
  repository and read `git diff --stat site/`. Anything you did not intend is
  the bug.

## The Claude Code skills live here

`skills/appsite`, `skills/appsite-bump` and `skills/appsite-legal` are the source of the
`/appsite`, `/appsite-bump` and `/appsite-legal` skills (moved from `~/.claude` on 27 Sep
2026; `appsite-legal` — terms and privacy policy, Apple's EULA covered, three review
rounds — added 21 Oct 2026). `~/.claude/skills/<name>`
are symlinks made by `./install.sh`: edit the skills here, and re-run `install.sh`
only when a new skill folder is added.
