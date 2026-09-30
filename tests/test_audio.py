import wave

from pomodoro.audio import CHIMES, SAMPLE_RATE, STEP, export_chimes


def test_export_chimes_writes_mono_pcm_matching_sound_ts(tmp_path):
    paths = export_chimes(tmp_path)
    assert sorted(p.name for p in paths) == ["chime_break.wav", "chime_work.wav"]
    for kind, notes in CHIMES.items():
        with wave.open(str(tmp_path / f"chime_{kind}.wav")) as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (1, 2, SAMPLE_RATE)
            assert w.getnframes() == round(len(notes) * STEP * SAMPLE_RATE)
            frames = w.readframes(w.getnframes())
        peak = max(abs(int.from_bytes(frames[i:i + 2], "little", signed=True)) for i in range(0, len(frames), 2))
        assert 0.3 * 32767 < peak <= 32767  # audible, not clipped past full scale
