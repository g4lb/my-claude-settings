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
