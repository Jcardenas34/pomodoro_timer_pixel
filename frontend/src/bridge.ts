/**
 * Typed access to the Python API (window.pywebview.api). On Android, and in a
 * plain browser (npm run dev from WSL, screenshots), LocalBackend (local.ts)
 * stands in, storing data on the device and loading bundled public/demo art.
 */

import { isNative, LocalBackend } from "./local";

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

export type BackgroundEffect = "petals" | "jacaranda" | "leaves" | "snow" | "mist" | "fireflies";

export interface BackgroundMeta {
  groundTop: number;
  groundBottom: number;
  /** Legacy flag from before `effect`; same as effect: "petals". */
  petals?: boolean;
  effect?: BackgroundEffect;
  /** Scene pixel where the effect originates (mist: the top of the Jet d'Eau). */
  effectOrigin?: [number, number];
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

/** Resolve the Python API once pywebview has injected it, or fall back to the in-page backend. */
export function connect(timeoutMs = 1500): Promise<Backend> {
  return new Promise((resolve) => {
    if (isNative()) return resolve(new LocalBackend()); // Android: no Python host
    if (window.pywebview?.api) return resolve(window.pywebview.api);
    const timer = setTimeout(() => resolve(new LocalBackend()), timeoutMs);
    window.addEventListener("pywebviewready", () => {
      clearTimeout(timer);
      resolve(window.pywebview!.api);
    });
  });
}
