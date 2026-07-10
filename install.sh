#!/usr/bin/env bash
# nightshift installer — safe to read before you run it.
#   curl -fsSL https://night-shift.sh/install | bash
#
# What this does, in order:
#   1. downloads nightshift into ~/.local/share/nightshift  (git clone, or tarball)
#   2. symlinks the `nightshift` command into ~/.local/bin
#   3. runs `nightshift init` so it's ready to use
#   4. `git init`s your journal (~/.nightshift) so your thinking is versioned from entry one
#   5. offers to star the repo (only with your yes; needs the `gh` CLI)
#   6. sends ONE anonymous install ping (a tally, no PII) — opt out with NIGHTSHIFT_NO_TELEMETRY=1
#
# Everything is overridable by env var. Nothing runs as root. No sudo.
set -euo pipefail

REPO_SLUG="KonstantCloud/nightshift"
REPO_URL="https://github.com/${REPO_SLUG}"
TARBALL="https://github.com/${REPO_SLUG}/archive/refs/heads/main.tar.gz"
# canonical site. change this one line if the domain changes.
SITE="${NIGHTSHIFT_SITE:-https://night-shift.sh}"
PING_URL="${SITE}/api/i"

SRC="${NIGHTSHIFT_SRC:-$HOME/.local/share/nightshift}"
BINDIR="${NIGHTSHIFT_BIN:-$HOME/.local/bin}"
NS_HOME="${NIGHTSHIFT_HOME:-$HOME/.nightshift}"

c_amber='\033[38;5;214m'; c_dim='\033[2m'; c_reset='\033[0m'; c_bold='\033[1m'
say(){ printf "${c_amber}▸${c_reset} %s\n" "$*"; }
dim(){ printf "${c_dim}  %s${c_reset}\n" "$*"; }
# [ -r /dev/tty ] lies in CI/containers (perms ok, open fails) — test actual openability once
if ( : </dev/tty ) 2>/dev/null; then HAS_TTY=1; else HAS_TTY=; fi
tty_read(){ if [ -n "$HAS_TTY" ]; then read -r "$@" </dev/tty; else return 1; fi; }

printf "\n${c_bold}${c_amber}nightshift${c_reset} ${c_dim}— an encrypted, multi-session work journal for AI coding agents${c_reset}\n\n"

# --- 1. fetch source ---------------------------------------------------------
if command -v git >/dev/null 2>&1; then
  if [ -d "$SRC/.git" ]; then
    say "updating $SRC"
    git -C "$SRC" pull --ff-only --quiet || { say "update failed — re-cloning"; rm -rf "$SRC"; git clone --depth 1 --quiet "$REPO_URL" "$SRC"; }
  else
    say "cloning into $SRC"; rm -rf "$SRC"; git clone --depth 1 --quiet "$REPO_URL" "$SRC"
  fi
else
  command -v curl >/dev/null 2>&1 || { echo "need curl or git"; exit 1; }
  say "downloading into $SRC (no git found)"; rm -rf "$SRC"; mkdir -p "$SRC"
  curl -fsSL "$TARBALL" | tar -xz --strip-components=1 -C "$SRC"
fi

# --- 2. put `nightshift` on PATH --------------------------------------------
mkdir -p "$BINDIR"
ln -sf "$SRC/bin/nightshift" "$BINDIR/nightshift"
say "linked ${BINDIR}/nightshift"
case ":$PATH:" in
  *":$BINDIR:"*) ;;
  *) dim "note: $BINDIR is not on your PATH — add:  export PATH=\"$BINDIR:\$PATH\"" ;;
esac

# --- 3. dependency check -----------------------------------------------------
missing=""
for d in jq python3; do command -v "$d" >/dev/null 2>&1 || missing="$missing $d"; done
[ -n "$missing" ] && dim "missing (install for full function):$missing"
python3 -c "import cryptography" >/dev/null 2>&1 || dim "optional: 'pip install cryptography' enables the encrypted page"

# --- 4. initialize -----------------------------------------------------------
say "initializing $NS_HOME"
if [ -n "$HAS_TTY" ]; then "$BINDIR/nightshift" init </dev/tty; else "$BINDIR/nightshift" init; fi

# --- 5. version your journal (git init the home) -----------------------------
if command -v git >/dev/null 2>&1 && [ ! -d "$NS_HOME/.git" ]; then
  git -C "$NS_HOME" init --quiet   # init already wrote a .gitignore covering .password + the render
  git -C "$NS_HOME" add -A >/dev/null 2>&1 || true
  git -C "$NS_HOME" -c user.email=you@nightshift -c user.name=nightshift commit -qm "nightshift: initial journal" >/dev/null 2>&1 || true
  say "your journal is now a git repo ($NS_HOME) — push it to a PRIVATE remote to keep the record"
  dim "entries are stored in plaintext; only the rendered page is encrypted"
fi

# --- 6. wire your agent (prompted, default yes) ------------------------------
if [ -n "$HAS_TTY" ] && [ -d "$HOME/.claude" ]; then
  if command -v jq >/dev/null 2>&1; then
    printf "${c_dim}  Claude Code detected — wire the hooks now (Stop-hook enforcement)? [Y/n] ${c_reset}"
    ans=""; tty_read ans || true
    case "$ans" in n|N|no|NO) dim "later: bash $SRC/adapters/claude-code/install.sh" ;;
      *) bash "$SRC/adapters/claude-code/install.sh" ;; esac
  else
    dim "Claude Code detected but jq is missing — install jq, then: bash $SRC/adapters/claude-code/install.sh"
  fi
fi
[ -d "$HOME/.codex" ] && dim "Codex detected — see $SRC/adapters/codex/README.md to wire its hooks"

# --- 7. star (opt-in, needs gh) ---------------------------------------------
if [ -n "$HAS_TTY" ]; then
  printf "${c_dim}  star %s on GitHub? [y/N] ${c_reset}" "$REPO_SLUG"
  ans=""; tty_read ans || true
  case "$ans" in
    y|Y|yes|YES)
      if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
        gh api --method PUT "/user/starred/${REPO_SLUG}" >/dev/null 2>&1 && say "starred — thank you" || dim "couldn't star via gh; do it here: ${REPO_URL}"
      else
        dim "no authed gh CLI — star here: ${REPO_URL}"
      fi ;;
    *) : ;;
  esac
fi

# --- 8. anonymous install ping (opt out: NIGHTSHIFT_NO_TELEMETRY=1) -----------
if [ -z "${NIGHTSHIFT_NO_TELEMETRY:-}" ] && command -v curl >/dev/null 2>&1; then
  curl -fsS -m 4 -X POST "$PING_URL" -H 'content-type: application/json' \
    -d '{"source":"install.sh"}' >/dev/null 2>&1 || true
fi

# --- done --------------------------------------------------------------------
cat <<EOF

$(printf "${c_bold}installed.${c_reset}")  next:

  $(printf "${c_amber}nightshift log diary demo${c_reset}") "first entry — testing the thing"
  $(printf "${c_amber}nightshift render${c_reset}")              # -> $NS_HOME/index.html

  wire the enforcement into your agent (Claude Code / Codex):
    $(printf "${c_dim}bash $SRC/adapters/claude-code/install.sh${c_reset}")
    $(printf "${c_dim}see  $SRC/adapters/codex/README.md${c_reset}")

  docs: ${SITE}    source: ${REPO_URL}

EOF
