"""The name half of a Lemon-ID: a random WordyBin, or whatever `[brief] name` prints.

lemonaid only needs a name to be short, unlikely to repeat, and safe in a Lemon-ID
and in the shell commands briefs hand to lemons. `[brief] name` is a shell command
printing one, for someone who wants their lemons named another way; the first word
it prints is the name. A name another lemon holds is asked for again, as a WordyBin is.
"""

import os
import re
import subprocess

import wordybin

from ..config import load_config

_TIMEOUT_SECONDS = 5
# No dot, which splits a Lemon-ID's slug from its name, and nothing a shell quotes.
_NAME = re.compile(r"[\w-]+")


def _command() -> str:
    return load_config().brief.name.strip()


def _checked(name: str, source: str) -> str:
    if not _NAME.fullmatch(name):
        raise ValueError(f"{source} gave {name!r}; a name is letters, digits, _ and - only")

    return name


def new() -> str:
    """A fresh name; raises ValueError when `[brief] name` fails or prints a bad one."""
    command = _command()
    if not command:
        return wordybin.encode(os.urandom(2))

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=_TIMEOUT_SECONDS
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        raise ValueError(f"[brief] name {command!r} failed to run: {e}") from None

    name = next(iter(result.stdout.split()), "")
    if result.returncode != 0 or not name:
        raise ValueError(f"[brief] name {command!r} printed no name: {result.stderr.strip()}")

    return _checked(name, f"[brief] name {command!r}")


def chosen(name: str) -> str:
    """*name*, picked by hand, as a Lemon-ID spells it; raises ValueError if it can't be one.

    With `[brief] name` unset it must be a two-word WordyBin, in any case. With it set,
    lemonaid can't tell what the command would print, so any safe name is taken as written.
    """
    if _command():
        return _checked(name, "--set")

    decoded = wordybin.decode(name)
    if len(decoded) != 2:
        raise ValueError(f"{name!r} is not a two-word WordyBin")

    return wordybin.encode(decoded)
