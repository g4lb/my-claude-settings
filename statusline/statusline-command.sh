#!/bin/bash
# Claude Code status line
# Shows: model name | git branch (if any) | worktree (if linked) | current working directory | account email
# Colors are dimmed to suit Claude Code's status line rendering.

input=$(cat)

# Per-session tab color / background tint / badge in iTerm2 (no-op when unchanged).
# Optional: runs only if session-look.py is installed.
if [ -f "$HOME/.claude/session-look.py" ]; then
  printf '%s' "$input" | python3 "$HOME/.claude/session-look.py" apply >/dev/null 2>&1 &
fi

model=$(echo "$input" | jq -r '.model.display_name // empty')
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // empty')

# Git branch, if cwd is inside a git repo. --no-optional-locks avoids
# contending with concurrent git operations in the same repo/worktree.
branch=""
worktree=""
if git -C "$cwd" --no-optional-locks rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  branch=$(git -C "$cwd" --no-optional-locks branch --show-current 2>/dev/null)

  # A linked worktree has a git-dir that differs from the repo's common
  # git-dir; the main checkout's git-dir and common-dir are the same.
  git_dir=$(git -C "$cwd" --no-optional-locks rev-parse --git-dir 2>/dev/null)
  common_dir=$(git -C "$cwd" --no-optional-locks rev-parse --git-common-dir 2>/dev/null)
  if [ -n "$git_dir" ] && [ -n "$common_dir" ]; then
    git_dir_abs=$(cd "$cwd" && cd "$(dirname "$git_dir")" 2>/dev/null && pwd)/$(basename "$git_dir")
    common_dir_abs=$(cd "$cwd" && cd "$(dirname "$common_dir")" 2>/dev/null && pwd)/$(basename "$common_dir")
    if [ "$git_dir_abs" != "$common_dir_abs" ]; then
      toplevel=$(git -C "$cwd" --no-optional-locks rev-parse --show-toplevel 2>/dev/null)
      [ -n "$toplevel" ] && worktree=$(basename "$toplevel")
    fi
  fi
fi

DIM="\033[2m"
RESET="\033[0m"
CYAN="\033[2;36m"
GREEN="\033[2;32m"
MAGENTA="\033[2;35m"
YELLOW="\033[2;33m"
BLUE="\033[94m"

# Logged-in account email: prefer the stdin JSON (if a future version adds it),
# otherwise read oauthAccount.emailAddress from ~/.claude.json at run time.
# Only that one field is extracted; nothing else from the file is used.
email=$(echo "$input" | jq -r '.account.email // .email // empty' 2>/dev/null)
if [ -z "$email" ] && [ -r "$HOME/.claude.json" ]; then
  email=$(jq -r '.oauthAccount.emailAddress // empty' "$HOME/.claude.json" 2>/dev/null)
fi

out=""
[ -n "$model" ] && out="${CYAN}${model}${RESET}"
if [ -n "$branch" ]; then
  [ -n "$out" ] && out="${out} ${DIM}|${RESET} "
  out="${out}${GREEN}${branch}${RESET}"
fi
if [ -n "$worktree" ]; then
  [ -n "$out" ] && out="${out} ${DIM}|${RESET} "
  out="${out}${MAGENTA}wt:${worktree}${RESET}"
fi
if [ -n "$cwd" ]; then
  [ -n "$out" ] && out="${out} ${DIM}|${RESET} "
  out="${out}${YELLOW}${cwd}${RESET}"
fi
if [ -n "$email" ]; then
  [ -n "$out" ] && out="${out} ${DIM}|${RESET} "
  out="${out}${BLUE}${email}${RESET}"
fi

printf "%b" "$out"
