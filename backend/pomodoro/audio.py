"""Render the frontend's 8-bit chimes (frontend/src/sound.ts) to WAV files.

Android plays these as notification sounds when a phase ends while the app is
hidden, so they must match the WebAudio chime note for note.
"""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

# Same tables as sound.ts: notes (Hz) played STEP seconds apart, each decaying
# exponentially from GAIN to FLOOR over DECAY seconds.
CHIMES = {
    "work": [1047, 784, 659, 784],
    "break": [659, 784, 1047],
}
STEP = 0.14
DECAY = 0.13
GAIN = 0.08
FLOOR = 0.001
SAMPLE_RATE = 44100
# WebAudio's 0.08 is quiet next to other notification sounds; scale the whole
# waveform up without changing its shape.
PEAK = 0.5


def render(notes: list[int], rate: int = SAMPLE_RATE) -> list[float]:
    """Samples in [-1, 1] for a square-wave arpeggio."""
    samples = [0.0] * round(len(notes) * STEP * rate)
    for i, freq in enumerate(notes):
        start = round(i * STEP * rate)
        for n in range(round(STEP * rate)):
            t = n / rate
            gain = GAIN * (FLOOR / GAIN) ** min(t / DECAY, 1.0)
            square = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
            samples[start + n] += gain * square
    return [s * PEAK / GAIN for s in samples]


def write_wav(path: Path, samples: list[float], rate: int = SAMPLE_RATE) -> None:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"".join(struct.pack("<h", round(max(-1.0, min(1.0, s)) * 32767)) for s in samples))


def export_chimes(out_dir: Path) -> list[Path]:
    """Write chime_work.wav and chime_break.wav (Android res/raw names) to out_dir."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for kind, notes in CHIMES.items():
        path = out_dir / f"chime_{kind}.wav"
        write_wav(path, render(notes))
        paths.append(path)
    return paths
