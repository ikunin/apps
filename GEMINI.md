# Maintaining the app sites

**Read [AGENTS.md](AGENTS.md).** It is the maintained copy; this file exists so
that an agent looking for its own filename finds it.

Two things not to guess at, before you touch anything:

- **Never copy a privacy or terms sentence from one app to another.** The three
  apps differ in what they collect, and a copied claim is a false statement.
  AGENTS.md has the table.
- **Run both checkers before publishing** — `check_text.py` and `make site`.
  Between them they have caught four published bugs.
