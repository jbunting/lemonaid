# cmux Integration

Lemonaid switches to the [cmux](https://cmux.com) workspace and surface (tab) where a notification came from, and resumes the session in a new workspace when it has none. There is nothing to configure.

## How it works

A hook run inside cmux sees `CMUX_SURFACE_ID` and records the notification with `switch_source = "cmux"`, the session's tty, and its surface (`cmux_surface`). Selecting it in `lma`, and the watcher deciding whether it has ended, both find the session by one rule:

1. **The recorded surface, while it still has the recorded tty.** Either alone can pass to something else: a tty name to another surface, a surface to another program.
2. **A surface cmux has bound to the session, where its agent (`claude`, `codex`, ...) runs.** cmux records the agent session each surface runs, and resumes it there after a restart, on a new tty. A binding outlives its agent, which is why the agent has to be running.
3. **For a row recorded without a surface, the surface with its tty.**

A session run in tmux inside cmux is recorded as tmux, and is switched to by the [tmux integration](tmux.md).

### Switching

Selecting a notification, or an archived session in history, uses the rule too. In history, a session the rule finds running is brought back to the inbox rather than resumed a second time.

Selecting a notification focuses the surface found with `cmux focus-panel`, which also brings its workspace forward. When the session runs on more than one surface, lemonaid does nothing, since resuming would make a third copy. When it runs on none, lemonaid resumes it with its harness's resume command (see `resume_command` in [config.md](config.md)) in a new workspace rooted at its directory. A session with no resume command, or whose directory is gone, is left alone. If `ps` cannot say what runs on a surface, lemonaid neither switches nor resumes.

### The watcher

The watcher asks `cmux tree --all` once per tick, with a half-second timeout. Step 2 needs a `cmux list-panels` for each workspace, about 0.7 s for 30 of them, so it runs only for a session that is not where it was recorded, and the watcher reuses that answer for 10 seconds. A session found on another tty is judged there; a session found nowhere is archived. If cmux does not answer, nothing is archived, and that is logged once until cmux answers again.

## Requirements

Lemonaid calls the `cmux` CLI, so it must be on `PATH` and able to reach the cmux socket. Processes started inside cmux can; for anything else, see cmux's socket settings (`cmux docs settings`).

## Where to run `lma`

Run it in the cmux Dock, the right sidebar. cmux keeps a Dock for each window as well as for each workspace, and the window's Dock stays in view whichever workspace is selected. That is the job the [tmux scratch pane and follow mode](tmux.md#scratch-pane) do, so cmux needs neither.

Run in cmux, `lma` shows only the notifications from cmux, plus headless ones, as it does for tmux and WezTerm.

## Limitations

- **No back navigation.** There is no `lemonaid cmux back` yet.
- **tmux-only features stay tmux-only:** the brief sidebar and session templates. A resumed session gets a plain workspace, not a template's layout.
