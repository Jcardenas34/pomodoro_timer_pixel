import { describe, expect, it } from "vitest";
import { DEFAULT_SETTINGS, LocalBackend, type KV } from "./local";

function memoryKV(): KV & { data: Map<string, string> } {
  const data = new Map<string, string>();
  return {
    data,
    async get(key) {
      return data.get(key) ?? null;
    },
    async set(key, value) {
      data.set(key, value);
    },
  };
}

function setup() {
  let now = 1_000_000;
  const kv = memoryKV();
  const api = new LocalBackend(kv, () => now);
  return { kv, api, tick: (s: number) => (now += s) };
}

describe("LocalBackend", () => {
  it("merges settings over defaults and ignores unknown keys", async () => {
    const { kv, api } = setup();
    const saved = await api.save_settings({ frameColor: "#ff0000", bogus: 1 } as never);
    expect(saved).toEqual({ ...DEFAULT_SETTINGS, frameColor: "#ff0000" });
    // A fresh instance over the same store sees the saved value (survives an app restart).
    const reopened = new LocalBackend(kv);
    expect((await reopened.save_settings({})).frameColor).toBe("#ff0000");
  });

  it("aggregates work sessions per task like storage.py", async () => {
    const { api, tick } = setup();
    const a = await api.start_session("Write", "work");
    await api.end_session(a, 1500, true);
    const b = await api.start_session("  Write ", "work");
    await api.end_session(b, 300, false);
    const c = await api.start_session(null, "work");
    await api.end_session(c, 60, true);
    const brk = await api.start_session("Write", "short");
    await api.end_session(brk, 300, true);
    tick(60);

    expect(new Set([a, b, c, brk]).size).toBe(4);
    expect(await api.get_stats(7)).toEqual([
      { task: "Write", seconds: 1800, pomodoros: 1 },
      { task: "(no task)", seconds: 60, pomodoros: 1 },
    ]);
  });

  it("leaves sessions older than the window out of stats", async () => {
    const { api, tick } = setup();
    const old = await api.start_session("Old", "work");
    await api.end_session(old, 1500, true);
    tick(8 * 86400);
    expect(await api.get_stats(7)).toEqual([]);
  });
});
