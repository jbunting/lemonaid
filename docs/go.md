# Jump to a lemon

`lemonaid go` switches to a lemon: an attached tmux client to the lemon's
recorded pane, or cmux to the lemon's surface:

```bash
lemonaid go lemonaid-go.OzoneYes
lemonaid go codex:019abcdef-0123-4567-8901-234567890abc
lemonaid go 'lemonaid://go/lemonaid-go.OzoneYes'
lemonaid go lemonaid-go.OzoneYes --link
```

`--link` prints the target as an OSC 8 hyperlink to `lemonaid://go/<target>`.
It only formats the link, so another lemon can print it without resolving the
recipient. Markdown-capable renderers can use
`[go to the lemon](lemonaid://go/lemonaid-go.OzoneYes)` instead.

In the inbox's brief view, every Lemon-ID is a `lemonaid://go/<Lemon-ID>` link:
the `Brief-ID:` and `Parent:` lines, the children list, and any ID lemonaid has
registered (or rerolled away from) in the brief's text, bare or alone in backticks.
Text shaped like an ID that lemonaid doesn't know stays plain. Clicking needs the
URL handler below. `lemonaid brief show` prints plain text and is unchanged.

A Lemon-ID follows its attached brief and supports rerolled ID aliases. A channel
also works without a brief. Row order, folding, read state and snoozing do not
change the target. Jumping leaves the inbox state alone. An archived row, a
missing pane or surface, or a lemon in another terminal produces an error; this
command does not resume or start a lemon. Hooks record pane IDs scoped to the tmux
server lifetime; existing sessions need a notification from the updated hooks
before their first jump. A record without that pane identity fails closed.

After a jump, you can return to the sender by clicking its inbox row or selecting
it and pressing Enter. The inbox cursor may still be on the sender; the green
bar follows the terminal currently on screen. If older rows share that terminal's
TTY, only its latest notification gets the bar.

## cmux

A cmux lemon's surface is found by the same rule the inbox uses on Enter (see
[cmux](cmux.md)), and cmux focuses it, bringing its workspace forward. Where the
inbox would resume a lemon that has no surface, `lemonaid go` refuses: a stray
click shouldn't start a session. It also refuses when several surfaces run the
lemon, or when it can't tell which one does. `--client` is for tmux only.

## Future terminal support

WezTerm and pluggable terminal backends are possible future extensions: links
identify lemons rather than terminals, so existing links keep working when
another backend is added.

## Which tmux client moves

The recorded tmux socket selects the server. From a pane on that server, the
command chooses the sole client viewing any session containing the caller's
pane. A window shared across sessions considers clients in all of them. Outside tmux,
including a macOS URL handler, it chooses the sole attached client on the target
server. With zero or multiple matching clients it refuses to guess.

List attached clients and choose an exact name when needed:

```bash
tmux list-clients -F '#{client_name} #{session_name}'
lemonaid go lemonaid-go.OzoneYes --client /dev/ttys005
```

For a separate server, run the list command with `tmux -S /path/to/socket`.
A jump changes what the chosen client displays; it does not focus an OS window.

## iTerm2 on macOS

This release provides the CLI and a documented handler setup, without installing
an app or changing terminal settings. iTerm2 supports
[OSC 8 hyperlinks](https://iterm2.com/documentation-escape-codes.html), and macOS
registers application URL schemes through
[`CFBundleURLTypes`](https://developer.apple.com/documentation/bundleresources/information-property-list/cfbundleurltypes).

1. Enable hyperlinks for your outer terminal in tmux 3.4 or newer. Add this to
   `~/.tmux.conf` using the appropriate `TERM` pattern, then reload it:

   ```tmux
   set -as terminal-features ',xterm*:hyperlinks'
   ```

2. Open Script Editor and create this script. Replace the lemonaid path
   with the absolute path printed by `command -v lemonaid`, and use
   `command -v tmux` to find the directory to include in PATH. GUI apps do not inherit your shell's PATH.

   ```applescript
   on open location jumpURL
       try
           do shell script "PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin " & quoted form of "/Users/YOU/.local/bin/lemonaid" & " go " & quoted form of jumpURL
       on error messageText
           display alert "Lemonaid jump failed" message messageText
       end try
   end open location
   ```

   Ensure PATH includes the directory containing your tmux executable. If you
   have several clients, append ` & " --client /dev/ttys005"` to the command,
   using the client you want the handler to move. A client name can change after
   reattaching, so update it when needed.

3. Save with **File Format: Application** as
   `~/Applications/Lemonaid Go.app`. Run the following in a POSIX shell (for
   example `zsh`), to register `lemonaid://` with that app:

   ```bash
   /usr/libexec/PlistBuddy -c 'Add :CFBundleURLTypes array' "$HOME/Applications/Lemonaid Go.app/Contents/Info.plist"
   /usr/libexec/PlistBuddy -c 'Add :CFBundleURLTypes:0 dict' "$HOME/Applications/Lemonaid Go.app/Contents/Info.plist"
   /usr/libexec/PlistBuddy -c 'Add :CFBundleURLTypes:0:CFBundleURLName string Lemonaid' "$HOME/Applications/Lemonaid Go.app/Contents/Info.plist"
   /usr/libexec/PlistBuddy -c 'Add :CFBundleURLTypes:0:CFBundleURLSchemes array' "$HOME/Applications/Lemonaid Go.app/Contents/Info.plist"
   /usr/libexec/PlistBuddy -c 'Add :CFBundleURLTypes:0:CFBundleURLSchemes:0 string lemonaid' "$HOME/Applications/Lemonaid Go.app/Contents/Info.plist"
   codesign --force --sign - "$HOME/Applications/Lemonaid Go.app"
   /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$HOME/Applications/Lemonaid Go.app"
   ```

   These commands apply once to the newly saved app. To remove the handler,
   unregister with `lsregister -u` and move the app to Trash.

4. With one attached tmux client, print `lemonaid go <Lemon-ID> --link`, then
   Cmd-click the label in iTerm2. You can also test the handler with
   `open 'lemonaid://go/<Lemon-ID>'` from a shell. The selected client should
   display that lemon's pane. An error dialog reports unknown targets or
   ambiguous clients.

The handler passes the URL as one quoted argument; it does not run URL text as
shell code. The CLI validates the scheme, destination and target before switching.
Other terminal emulators can open the same scheme through this macOS handler if
they support OSC 8. No WezTerm-specific rule is installed by this release.

## cmux on macOS

cmux renders OSC 8 links itself, so it needs no terminal setting. Build the
handler app as in the iTerm2 steps above, with two changes to the script:
put cmux's CLI directory on PATH, and bring cmux to the front for links clicked
in other apps, such as Obsidian or a browser.

```applescript
on open location jumpURL
    try
        do shell script "PATH=/Applications/cmux.app/Contents/Resources/bin:/usr/bin:/bin " & quoted form of "/Users/YOU/.local/bin/lemonaid" & " go " & quoted form of jumpURL
        tell application id "com.cmuxterm.app" to activate
    on error messageText
        display alert "Lemonaid jump failed" message messageText
    end try
end open location
```
