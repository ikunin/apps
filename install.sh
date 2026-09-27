#!/bin/zsh
# Link this repository's Claude Code skills (skills/appsite, skills/appsite-bump)
# into ~/.claude/skills. The repository is their source (27 Sep): edit them here,
# and a change is live at once through the link; re-run this only for a new skill.
#
# A folder already at the link's place is moved aside, outside ~/.claude/skills:
# a backup left beside it would register as a second skill with the same name.

set -eu
REPO="${0:A:h}"
SKILLS="$HOME/.claude/skills"
ATTIC="$HOME/.claude/state/appsite/replaced"

for skill in "$REPO"/skills/*(/); do
  where="$SKILLS/${skill:t}"          # not `path`: in zsh that is tied to PATH
  if [[ -L "$where" ]]; then
    rm "$where"
  elif [[ -e "$where" ]]; then
    mkdir -p "$ATTIC"
    mv "$where" "$ATTIC/${skill:t}-$(date +%Y%m%d%H%M%S)"
    print "kept the old ${skill:t} in ${ATTIC/$HOME/~}"
  fi
  mkdir -p "$SKILLS"
  ln -s "$skill" "$where"
  print "linked ${where/$HOME/~} → ${skill/$HOME/~}"
done
