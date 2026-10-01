"""Putting a session back when selecting it finds no cmux surface for it.

Like the tmux recreate: the row's own session is resumed with its harness's
resume command, in its directory, and a row with no way to resume it is refused.
It opens in a workspace of its own.
"""

from pathlib import Path
from typing import Any

from ..config import Config
from ..log import get_logger
from ..resume import build_resume_command
from . import navigation

_log = get_logger("cmux.recreate")


def recreate(metadata: dict[str, Any], config: Config) -> bool:
    """Resume the notification's session in a new cmux workspace rooted at its cwd."""
    cwd = metadata.get("cwd")
    if not cwd or not Path(cwd).is_dir():
        return False

    channel = metadata.get("channel", "")
    resumable = build_resume_command(config, channel, metadata)
    if resumable is None:
        _log.warning("not recreating %s: no way to resume it", channel or "a session")
        return False

    _, argv = resumable
    return navigation.open_workspace(cwd, argv, metadata.get("name") or Path(cwd).name)
