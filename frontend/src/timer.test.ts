import { describe, expect, it } from "vitest";
import { PomodoroTimer, type TimerConfig, type TimerEvent } from "./timer";

const cfg: TimerConfig = {
  workMinutes: 25,
  shortMinutes: 5,
  longMinutes: 15,
  longEvery: 4,
  autoStartBreaks: true,
  autoStartWork: false,
};

function setup(overrides: Partial<TimerConfig> = {}) {
  let t = 0;
  const timer = new PomodoroTimer({ ...cfg, ...overrides }, () => t);
  const events: TimerEvent[] = [];
  timer.on((e) => events.push(e));
  const advance = (ms: number) => {
    t += ms;
    timer.tick();
  };
  return { timer, events, advance };
}

describe("PomodoroTimer", () => {
  it("counts down from the work duration", () => {
    const { timer, advance } = setup();
    expect(timer.remainingMs()).toBe(25 * 60_000);
    timer.start();
    advance(60_000);
    expect(timer.remainingMs()).toBe(24 * 60_000);
  });

  it("keeps remaining time across pause and resume", () => {
    const { timer, advance } = setup();
    timer.start();
    advance(10_000);
    timer.pause();
    advance(500_000); // time passes while paused
    expect(timer.remainingMs()).toBe(25 * 60_000 - 10_000);
    timer.start();
    advance(5_000);
    expect(timer.remainingMs()).toBe(25 * 60_000 - 15_000);
  });

  it("completes work, auto-starts the short break, waits before next work", () => {
    const { timer, events, advance } = setup();
    timer.start();
    advance(25 * 60_000);
    expect(events.map((e) => e.type)).toEqual(["start", "complete", "start"]);
    expect(timer.phase).toBe("short");
    expect(timer.status).toBe("running");
    advance(5 * 60_000);
    expect(timer.phase).toBe("work");
    expect(timer.status).toBe("idle");
  });

  it("takes a long break after every 4th work phase, then restarts the cycle", () => {
    const { timer, advance } = setup({ autoStartWork: true });
    const phases: string[] = [];
    timer.on((e) => e.type === "start" && phases.push(e.phase));
    timer.start();
    for (let i = 0; i < 8; i++) advance(timer.durationMs());
    expect(phases).toEqual(["work", "short", "work", "short", "work", "short", "work", "long", "work"]);
  });

  it("reports elapsed time when a started phase is reset", () => {
    const { timer, events, advance } = setup();
    timer.start();
    advance(90_000);
    timer.reset();
    expect(events.at(-1)).toEqual({ type: "abort", phase: "work", elapsedMs: 90_000 });
    expect(timer.status).toBe("idle");
    expect(timer.remainingMs()).toBe(25 * 60_000);
  });

  it("skip moves to the break without auto-starting it", () => {
    const { timer } = setup();
    timer.skip();
    expect(timer.phase).toBe("short");
    expect(timer.status).toBe("idle");
  });

  it("applies new durations only before the phase starts", () => {
    const { timer, advance } = setup();
    timer.configure({ ...cfg, workMinutes: 50 });
    expect(timer.remainingMs()).toBe(50 * 60_000);
    timer.start();
    advance(1_000);
    timer.configure({ ...cfg, workMinutes: 10 });
    expect(timer.remainingMs()).toBe(50 * 60_000 - 1_000);
  });
});
