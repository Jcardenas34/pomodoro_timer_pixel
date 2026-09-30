export type Phase = "work" | "short" | "long";
export type Status = "idle" | "running" | "paused";

export interface TimerConfig {
  workMinutes: number;
  shortMinutes: number;
  longMinutes: number;
  longEvery: number;
  autoStartBreaks: boolean;
  autoStartWork: boolean;
}

export type TimerEvent =
  | { type: "start"; phase: Phase }
  | { type: "complete"; phase: Phase; elapsedMs: number }
  | { type: "abort"; phase: Phase; elapsedMs: number };

/**
 * Pomodoro state machine. Time is derived from a deadline (endsAt) rather than
 * counting ticks, so it never drifts even if frames are dropped.
 */
export class PomodoroTimer {
  phase: Phase = "work";
  status: Status = "idle";
  /** Completed work phases in the current cycle. */
  worksDone = 0;

  private endsAt = 0;
  private pausedRemaining = 0;
  private started = false; // has the current phase begun at all?
  private listeners: ((e: TimerEvent) => void)[] = [];

  constructor(
    private cfg: TimerConfig,
    private now: () => number = () => performance.now(),
  ) {
    this.pausedRemaining = this.durationMs();
  }

  on(fn: (e: TimerEvent) => void): void {
    this.listeners.push(fn);
  }

  private emit(e: TimerEvent): void {
    for (const fn of this.listeners) fn(e);
  }

  durationMs(phase: Phase = this.phase): number {
    const minutes = { work: this.cfg.workMinutes, short: this.cfg.shortMinutes, long: this.cfg.longMinutes }[phase];
    return Math.round(minutes * 60_000);
  }

  remainingMs(): number {
    if (this.status === "running") return Math.max(0, this.endsAt - this.now());
    return this.pausedRemaining;
  }

  elapsedMs(): number {
    return this.durationMs() - this.remainingMs();
  }

  /** Apply new settings. Resets the display only if the phase hasn't started. */
  configure(cfg: TimerConfig): void {
    this.cfg = cfg;
    if (!this.started) this.pausedRemaining = this.durationMs();
  }

  start(): void {
    if (this.status === "running") return;
    this.endsAt = this.now() + this.pausedRemaining;
    this.status = "running";
    if (!this.started) {
      this.started = true;
      this.emit({ type: "start", phase: this.phase });
    }
  }

  pause(): void {
    if (this.status !== "running") return;
    this.pausedRemaining = this.remainingMs();
    this.status = "paused";
  }

  toggle(): void {
    if (this.status === "running") this.pause();
    else this.start();
  }

  /** Restart the current phase from its full duration. */
  reset(): void {
    this.abortIfStarted();
    this.enter(this.phase, false);
  }

  /** Abandon the current phase and move to the next one. */
  skip(): void {
    this.abortIfStarted();
    this.advance(false);
  }

  /** Call every frame. Handles phase completion. */
  tick(): void {
    if (this.status === "running" && this.remainingMs() <= 0) {
      const phase = this.phase;
      this.emit({ type: "complete", phase, elapsedMs: this.durationMs() });
      if (phase === "work") this.worksDone++;
      this.advance(true);
    }
  }

  private abortIfStarted(): void {
    if (this.started) this.emit({ type: "abort", phase: this.phase, elapsedMs: this.elapsedMs() });
  }

  private advance(completed: boolean): void {
    let next: Phase;
    if (this.phase === "work") {
      const works = completed ? this.worksDone : this.worksDone + 1;
      next = works % this.cfg.longEvery === 0 ? "long" : "short";
      if (!completed) this.worksDone++;
    } else {
      next = "work";
      if (this.phase === "long") this.worksDone = 0;
    }
    const auto = next === "work" ? this.cfg.autoStartWork : this.cfg.autoStartBreaks;
    this.enter(next, completed && auto);
  }

  private enter(phase: Phase, autoStart: boolean): void {
    this.phase = phase;
    this.status = "idle";
    this.started = false;
    this.pausedRemaining = this.durationMs();
    if (autoStart) this.start();
  }
}
