"""Generate notification WAVs for GAPP-cli events.

Run with:
    uv run python scripts/gen_sounds.py
"""
import math
import os
import struct
import wave
from typing import List, Tuple

SAMPLE_RATE = 44100
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "gapp", "sounds")

# Each sound is a sequence of (freq Hz, duration s, volume 0..1, gap s after).
# gap = silence after the tone before the next one.
Tone = Tuple[float, float, float, float]

SOUNDS: "dict[str, List[Tone]]" = {
    # Ascending 3-tone arpeggio: clear "got a fix" cue.
    "position": [
        (1000.0, 0.090, 0.5, 0.030),
        (1200.0, 0.090, 0.5, 0.030),
        (1500.0, 0.130, 0.5, 0.000),
    ],
    # Two-tone "data" beep.
    "data": [
        (800.0, 0.080, 0.4, 0.030),
        (1000.0, 0.080, 0.4, 0.000),
    ],
    # Single short, low heartbeat tick.
    "heartbeat": [
        (600.0, 0.050, 0.3, 0.000),
    ],
}


def _render_tone(freq: float, duration: float, volume: float,
                 sample_rate: int = SAMPLE_RATE) -> bytes:
    n_samples = int(sample_rate * duration)
    amplitude = int(32767 * max(0.0, min(1.0, volume)))
    # Short fade in/out to avoid clicks (5 ms)
    fade = min(int(sample_rate * 0.005), n_samples // 2)
    frames = bytearray()
    for i in range(n_samples):
        env = 1.0
        if i < fade:
            env = i / fade
        elif i > n_samples - fade:
            env = (n_samples - i) / fade
        sample = int(amplitude * env * math.sin(2 * math.pi * freq * i / sample_rate))
        frames += struct.pack("<h", sample)
    return bytes(frames)


def _render_silence(duration: float, sample_rate: int = SAMPLE_RATE) -> bytes:
    return b"\x00\x00" * int(sample_rate * duration)


def _generate_sequence(path: str, tones: List[Tone],
                       sample_rate: int = SAMPLE_RATE) -> float:
    total_duration = 0.0
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit PCM
        wf.setframerate(sample_rate)
        for freq, dur, vol, gap in tones:
            wf.writeframes(_render_tone(freq, dur, vol, sample_rate))
            total_duration += dur
            if gap > 0:
                wf.writeframes(_render_silence(gap, sample_rate))
                total_duration += gap
    return total_duration


def main() -> None:
    out_dir = os.path.abspath(OUT_DIR)
    os.makedirs(out_dir, exist_ok=True)
    for name, tones in SOUNDS.items():
        path = os.path.join(out_dir, f"{name}.wav")
        total = _generate_sequence(path, tones)
        freqs = "+".join(f"{int(t[0])}Hz" for t in tones)
        print(f"wrote {path}  ({len(tones)} tone(s): {freqs}, {total*1000:.0f} ms)")


if __name__ == "__main__":
    main()
