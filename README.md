# my-claude-settings

My settings for Claude Code.

## Status line

The status line shows these items at the bottom of Claude Code:

```
Opus | main | wt:feature-x | /path/to/project | name@example.com
```

| Item | Content |
| --- | --- |
| Model | The model that Claude Code uses now |
| Branch | The git branch. It shows only in a git repository. |
| Worktree | The name of the linked worktree. It shows only in a linked worktree. |
| Folder | The current folder |
| Email | The email of the account that you use in Claude Code |

The script reads the email when it runs. Each user sees their own email.

### Install

Start Claude Code. Copy this prompt into it:

```
Install the status line from https://github.com/g4lb/my-claude-settings.

1. Check that jq is installed. If it is not installed, install it.
2. Download statusline/statusline-command.sh from the main branch.
3. Save it as ~/.claude/statusline-command.sh. Make it executable.
4. Read ~/.claude/settings.json. If the file does not exist, create it.
5. Add the statusLine setting from statusline/settings-snippet.json.
   Keep all other settings. If a statusLine setting exists, show it to me
   and ask before you replace it.
6. Run the script one time with test input, and show me the result.
```

Then start Claude Code again.

### Colors

The email is bright blue. The other items are dim. To change a color, edit the color lines in the script, for example `BLUE="\033[94m"`.

## Session look (iTerm2)

When you run many Claude Code sessions, it is easy to confuse them. The session look gives each session a different look in iTerm2:

| Item | Content |
| --- | --- |
| Tab color | Each open session gets a different color. Two open sessions do not get the same color (up to 8 sessions). |
| Background | A dark tint of the same color |
| Badge | The folder name, in small text at the top right of the window |

The status line script starts `session-look.py` each time that it updates. The script sends iTerm2 escape sequences only when something changes. When the session ends, a `SessionEnd` hook resets the tab color, the background, and the badge.

This works only in iTerm2. In other terminals, the escape sequences can have no effect.

### Install

Install the status line first. Then copy this prompt into Claude Code:

```
Install the session look from https://github.com/g4lb/my-claude-settings.

1. Download session-look/session-look.py from the main branch.
2. Save it as ~/.claude/session-look.py.
3. Make sure that ~/.claude/statusline-command.sh has the session-look block
   from statusline/statusline-command.sh. If it does not, add the block.
4. Read ~/.claude/settings.json. Add the SessionEnd hook from
   session-look/settings-snippet.json. Keep all other settings and hooks.
5. Show me the changes.
```

### Settings

To change the badge size, open iTerm2 and go to **Settings > Profiles > Default > General**. Next to **Badge**, click **Edit...**. Set **Max Height** to `0.05` and **Max Width** to `0.2`. A smaller number makes the text smaller. Scripts cannot change this setting. Only Claude Code tabs show a badge, so this change does not affect other tabs.

To change the colors, edit `PALETTE` in `session-look.py`.
