/**
 * Typed access to the Python API (window.pywebview.api). When the page runs in
 * a plain browser (npm run dev from WSL, screenshots), a mock backed by
 * localStorage and public/demo assets stands in.
 */

export interface Settings {
  frameColor: string;
  frameWidth: number;
  workMinutes: number;
  shortMinutes: number;
  longMinutes: number;
  longEvery: number;
  autoStartBreaks: boolean;
  autoStartWork: boolean;
  sound: boolean;
  background: string;
}

export interface BackgroundMeta {
  groundTop: number;
  groundBottom: number;
  petals?: boolean;
}

export type Direction = "down" | "up" | "right";

/** Overworld sprite sheet: per-direction walk cycles; "right" is mirrored for left. */
export interface SpriteMeta {
  frameWidth: number;
  frameHeight: number;
  fps: number;
  walk: Record<Direction, number[]>;
  idle: Record<Direction, number>;
}

export interface Asset<M = BackgroundMeta | SpriteMeta> {
  id: string;
  kind: "background" | "sprite";
  name: string;
  meta: M;
  active: boolean;
  src: string;
}

export interface AppState {
  settings: Settings;
  assets: Asset[];
}

export interface StatRow {
  task: string;
  seconds: number;
  pomodoros: number;
}

export interface Backend {
  get_state(): Promise<AppState>;
  save_settings(values: Partial<Settings>): Promise<Settings>;
  start_session(task: string | null, phase: string): Promise<number>;
  end_session(id: number, seconds: number, completed: boolean): Promise<void>;
  get_stats(days: number): Promise<StatRow[]>;
  toggle_fullscreen(): Promise<void>;
  quit(): Promise<void>;
}

declare global {
  interface Window {
    pywebview?: { api: Backend };
  }
}

const DEFAULT_SETTINGS: Settings = {
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
};

function readLocal<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    return raw ? { ...fallback, ...JSON.parse(raw) } : fallback;
  } catch {
    return fallback;
  }
}

function writeLocal(key: string, value: unknown): void {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* storage unavailable: settings just won't persist */
  }
}

class MockBackend implements Backend {
  private nextId = 1;

  async get_state(): Promise<AppState> {
    const res = await fetch("demo/manifest.json");
    const assets: Asset[] = res.ok ? await res.json() : [];
    return { settings: readLocal("settings", DEFAULT_SETTINGS), assets };
  }
  async save_settings(values: Partial<Settings>): Promise<Settings> {
    const merged = { ...readLocal("settings", DEFAULT_SETTINGS), ...values };
    writeLocal("settings", merged);
    return merged;
  }
  async start_session(task: string | null, phase: string): Promise<number> {
    console.info("[mock] start_session", task, phase);
    return this.nextId++;
  }
  async end_session(id: number, seconds: number, completed: boolean): Promise<void> {
    console.info("[mock] end_session", id, seconds, completed);
  }
  async get_stats(): Promise<StatRow[]> {
    return [];
  }
  async toggle_fullscreen(): Promise<void> {
    if (document.fullscreenElement) await document.exitFullscreen();
    else await document.documentElement.requestFullscreen();
  }
  async quit(): Promise<void> {}
}

/** Resolve the Python API once pywebview has injected it, or fall back to the mock. */
export function connect(timeoutMs = 1500): Promise<Backend> {
  return new Promise((resolve) => {
    if (window.pywebview?.api) return resolve(window.pywebview.api);
    const timer = setTimeout(() => resolve(new MockBackend()), timeoutMs);
    window.addEventListener("pywebviewready", () => {
      clearTimeout(timer);
      resolve(window.pywebview!.api);
    });
  });
}
