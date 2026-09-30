let ctx: AudioContext | null = null;

/** A short square-wave arpeggio, 8-bit style. No audio files needed. */
export function chime(kind: "work" | "break"): void {
  try {
    ctx ??= new AudioContext();
    const notes = kind === "break" ? [659, 784, 1047] : [1047, 784, 659, 784];
    notes.forEach((freq, i) => {
      const osc = ctx!.createOscillator();
      const gain = ctx!.createGain();
      const start = ctx!.currentTime + i * 0.14;
      osc.type = "square";
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(0.08, start);
      gain.gain.exponentialRampToValueAtTime(0.001, start + 0.13);
      osc.connect(gain).connect(ctx!.destination);
      osc.start(start);
      osc.stop(start + 0.14);
    });
  } catch {
    /* audio unavailable */
  }
}
