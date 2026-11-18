/**
 * Backend that lives entirely in the page: used on Android (Capacitor) and as
 * the browser fallback when pywebview is absent. Mirrors backend/pomodoro/storage.py:
 * settings merged over defaults, work sessions logged per task, stats grouped by task.
 */

import { App } from "@capacitor/app";
import { Capacitor } from "@capacitor/core";
import { Preferences } from "@capacitor/preferences";

import type { AppState, Asset, Backend, Settings, StatRow } from "./bridge";

export const DEFAULT_SETTINGS: Settings = {
  frameColor: "#000000",
  frameWidth: 6,
  workMinutes: 25,
  shortMinutes: 5,
  longMinutes: 15,
  longEvery: 4,
  autoStartBreaks: true,
  autoStartWork: false,
  sound: true,
  background: "builtin:fuji",
  sprite: "builtin:juan-sidepart",
  mustache: true,
};

export interface SessionRecord {
  id: number;
  task: string | null;
  phase: string;
  startedAt: number; // epoch seconds, like storage.py
  endedAt: number | null;
  seconds: number;
  completed: boolean;
}

/** Async key/value store. Preferences on Android survives WebView storage eviction. */
export interface KV {
  get(key: string): Promise<string | null>;
  set(key: string, value: string): Promise<void>;
}

export const browserKV: KV = {
  async get(key) {
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  },
  async set(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch {
      /* storage unavailable: data just won't persist */
    }
  },
};

export const nativeKV: KV = {
  async get(key) {
    return (await Preferences.get({ key })).value;
  },
  async set(key, value) {
    await Preferences.set({ key, value });
  },
};

export const isNative = (): boolean => Capacitor.isNativePlatform();

/** Same aggregation as Storage.stats: work phases since `since`, grouped by task, most time first. */
export function aggregateStats(sessions: SessionRecord[], since: number): StatRow[] {
  const byTask = new Map<string, StatRow>();
  for (const s of sessions) {
    if (s.phase !== "work" || s.startedAt < since) continue;
    const name = s.task ?? "(no task)";
    const row = byTask.get(name) ?? { task: name, seconds: 0, pomodoros: 0 };
    row.seconds += s.seconds;
    row.pomodoros += s.completed ? 1 : 0;
    byTask.set(name, row);
  }
  return [...byTask.values()].sort((a, b) => b.seconds - a.seconds);
}

export class LocalBackend implements Backend {
  constructor(
    private kv: KV = isNative() ? nativeKV : browserKV,
    private now: () => number = () => Date.now() / 1000,
  ) {}

  private async read<T>(key: string, fallback: T): Promise<T> {
    const raw = await this.kv.get(key);
    if (!raw) return fallback;
    try {
      return JSON.parse(raw) as T;
    } catch {
      return fallback;
    }
  }

  private async settings(): Promise<Settings> {
    return { ...DEFAULT_SETTINGS, ...(await this.read<Partial<Settings>>("settings", {})) };
  }

  private sessions(): Promise<SessionRecord[]> {
    return this.read<SessionRecord[]>("sessions", []);
  }

  private async saveSessions(sessions: SessionRecord[]): Promise<void> {
    await this.kv.set("sessions", JSON.stringify(sessions));
  }

  async get_state(): Promise<AppState> {
    let assets: Asset[] = [];
    try {
      const res = await fetch("demo/manifest.json");
      if (res.ok) assets = await res.json();
    } catch {
      /* no bundled art: scene stays blank */
    }
    return { settings: await this.settings(), assets };
  }

  async save_settings(values: Partial<Settings>): Promise<Settings> {
    const known = Object.fromEntries(Object.entries(values).filter(([k]) => k in DEFAULT_SETTINGS));
    const merged = { ...(await this.settings()), ...known };
    await this.kv.set("settings", JSON.stringify(merged));
    return merged;
  }

  async start_session(task: string | null, phase: string): Promise<number> {
    const sessions = await this.sessions();
    const id = sessions.reduce((max, s) => Math.max(max, s.id), 0) + 1;
    const name = task?.trim() || null;
    sessions.push({ id, task: name, phase, startedAt: this.now(), endedAt: null, seconds: 0, completed: false });
    await this.saveSessions(sessions);
    return id;
  }

  async end_session(id: number, seconds: number, completed: boolean): Promise<void> {
    const sessions = await this.sessions();
    const s = sessions.find((x) => x.id === id);
    if (!s) return;
    Object.assign(s, { endedAt: this.now(), seconds: Math.round(seconds), completed });
    await this.saveSessions(sessions);
  }

  async get_stats(days = 7): Promise<StatRow[]> {
    return aggregateStats(await this.sessions(), this.now() - days * 86400);
  }

  async toggle_fullscreen(): Promise<void> {
    if (isNative()) return; // Android runs immersive full screen already (MainActivity).
    if (document.fullscreenElement) await document.exitFullscreen();
    else await document.documentElement.requestFullscreen();
  }

  async quit(): Promise<void> {
    if (isNative()) await App.exitApp();
  }
}
