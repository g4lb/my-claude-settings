#!/usr/bin/env python3
"""Give each Claude Code session a distinct tab color and background tint in iTerm2.

  session-look.py apply   (stdin: status-line JSON)  -> tab color, bg tint
  session-look.py reset   (stdin: hook JSON)         -> restore defaults

Hook/status-line processes have no controlling terminal, so the escape
sequences are written to the tty of the nearest ancestor `claude` process.
Each live session picks a palette color that no other live session uses.
Never fails loudly: any error exits 0 silently.
"""

import json
import os
import subprocess
import sys

STATE_DIR = os.path.expanduser("~/.claude/session-look")

# (name, tab color, background tint for a dark theme)
PALETTE = [
    ("blue",    (59, 130, 246), (12, 20, 38)),
    ("green",   (34, 197, 94),  (10, 30, 18)),
    ("orange",  (249, 115, 22), (38, 20, 8)),
    ("purple",  (168, 85, 247), (28, 14, 40)),
    ("teal",    (20, 184, 166), (8, 30, 30)),
    ("pink",    (236, 72, 153), (38, 12, 26)),
    ("yellow",  (234, 179, 8),  (34, 28, 6)),
    ("red",     (239, 68, 68),  (40, 12, 12)),
]


def find_tty():
    pid = os.getppid()
    for _ in range(10):
        try:
            out = subprocess.run(["ps", "-o", "ppid=,tty=", "-p", str(pid)],
                                 capture_output=True, text=True, timeout=2).stdout.split()
        except (OSError, subprocess.SubprocessError):
            return None
        if len(out) < 2:
            return None
        ppid, tty = out[0], out[1]
        if tty not in ("??", "-"):
            return "/dev/" + tty
        pid = int(ppid)
        if pid <= 1:
            return None
    return None


def tty_alive(tty):
    """True if some `claude` process still runs on this tty."""
    try:
        out = subprocess.run(["ps", "-o", "comm=", "-t", os.path.basename(tty)],
                             capture_output=True, text=True, timeout=2).stdout
    except (OSError, subprocess.SubprocessError):
        return False
    return any(os.path.basename(l.strip()) == "claude" for l in out.splitlines())


def state_path(tty):
    return os.path.join(STATE_DIR, os.path.basename(tty) + ".json")


def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def pick_color(tty, session_id):
    used = set()
    for name in os.listdir(STATE_DIR):
        p = os.path.join(STATE_DIR, name)
        if p == state_path(tty):
            continue
        st = load(p)
        if not st:
            continue
        if tty_alive(st.get("tty", "")):
            used.add(st.get("color"))
        else:
            try:
                os.remove(p)  # stale: that session is gone
            except OSError:
                pass
    start = sum(session_id.encode()) % len(PALETTE)
    for i in range(len(PALETTE)):
        idx = (start + i) % len(PALETTE)
        if idx not in used:
            return idx
    return start


def osc(s):
    return "\033]" + s + "\007"


def apply(data):
    session_id = data.get("session_id") or ""
    cwd = (data.get("workspace") or {}).get("current_dir") or data.get("cwd") or ""
    sname = data.get("session_name") or ""
    tty = find_tty()
    if not tty or not session_id:
        return

    os.makedirs(STATE_DIR, exist_ok=True)
    project = os.path.basename(cwd.rstrip("/")) or cwd
    badge = project  # not shown; kept so a folder change still re-applies

    st = load(state_path(tty))
    if st and st.get("session_id") == session_id:
        if st.get("badge") == badge:
            return  # nothing changed: fast path
        color = st["color"]
    else:
        color = pick_color(tty, session_id)

    _, (tr, tg, tb), (br, bg, bb) = PALETTE[color]
    seq = (
        osc(f"6;1;bg;red;brightness;{tr}") +
        osc(f"6;1;bg;green;brightness;{tg}") +
        osc(f"6;1;bg;blue;brightness;{tb}") +
        osc(f"11;rgb:{br:02x}/{bg:02x}/{bb:02x}")
    )
    with open(tty, "w") as f:
        f.write(seq)
    with open(state_path(tty), "w") as f:
        json.dump({"session_id": session_id, "tty": tty, "color": color, "badge": badge}, f)


def reset(_data):
    tty = find_tty()
    if not tty:
        return
    with open(tty, "w") as f:
        f.write(osc("6;1;bg;*;default") + osc("111") + osc("1337;SetBadgeFormat="))
    try:
        os.remove(state_path(tty))
    except OSError:
        pass


def main():
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except (OSError, ValueError):
        data = {}
    action = sys.argv[1] if len(sys.argv) > 1 else "apply"
    {"apply": apply, "reset": reset}.get(action, apply)(data)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
