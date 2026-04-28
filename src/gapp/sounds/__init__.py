"""Non-blocking notification sound playback for GAPP-cli events.

Plays small WAV files shipped alongside this module via the first available
system audio player (``aplay``, ``paplay`` or ``ffplay``). If none is found,
calls become a silent no-op so the rest of the CLI is unaffected.
"""
import os
import shutil
import subprocess
import sys
import time
from typing import Dict, List, Optional

_SOUNDS_DIR = os.path.dirname(os.path.abspath(__file__))

# Resolved on first use.
_player_cmd: Optional[List[str]] = None
_player_resolved: bool = False

# Per-event last-played timestamps for simple rate limiting.
_last_played: Dict[str, float] = {}


def _resolve_player() -> Optional[List[str]]:
    """Pick the first available CLI audio player.

    Returns the argv prefix (without the file path) or ``None`` if no player
    is installed.
    """
    aplay = shutil.which("aplay")
    if aplay:
        return [aplay, "-q"]
    paplay = shutil.which("paplay")
    if paplay:
        return [paplay]
    ffplay = shutil.which("ffplay")
    if ffplay:
        return [ffplay, "-nodisp", "-autoexit", "-loglevel", "quiet"]
    return None


def play(event: str, min_interval: float = 0.0) -> None:
    """Asynchronously play the WAV associated with ``event``.

    Parameters
    ----------
    event:
        Sound name without extension, e.g. ``"position"``, ``"data"``,
        ``"heartbeat"``. The corresponding ``<event>.wav`` must exist in this
        package directory.
    min_interval:
        Minimum number of seconds between consecutive plays of the same
        event. Useful to throttle frequent triggers (e.g. heartbeat).
    """
    global _player_cmd, _player_resolved

    now = time.monotonic()
    if min_interval > 0:
        last = _last_played.get(event, 0.0)
        if now - last < min_interval:
            return
    _last_played[event] = now

    if not _player_resolved:
        _player_cmd = _resolve_player()
        _player_resolved = True
        if _player_cmd is None:
            print(
                "gapp.sounds: no audio player found (aplay/paplay/ffplay); "
                "notifications disabled.",
                file=sys.stderr,
            )

    if _player_cmd is None:
        return

    path = os.path.join(_SOUNDS_DIR, f"{event}.wav")
    if not os.path.isfile(path):
        return

    try:
        subprocess.Popen(
            _player_cmd + [path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            close_fds=True,
        )
    except Exception as e:
        print(f"gapp.sounds: failed to play {event}: {e}", file=sys.stderr)
