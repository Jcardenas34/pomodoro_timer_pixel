import "@fontsource/oswald/700.css";
import "@fontsource/press-start-2p/400.css";
import "./styles.css";

import { AndroidShell } from "./android";
import { connect, type Asset, type BackgroundMeta, type Settings, type SpriteMeta } from "./bridge";
import { FlipClock } from "./flipclock";
import { isNative } from "./local";
import { Scene } from "./scene";
import { chime } from "./sound";
import { PomodoroTimer, type Phase } from "./timer";
import { SettingsPanel, TaskPanel } from "./ui/panels";

const PHASE_LABEL: Record<Phase, string> = { work: "FOCUS", short: "SHORT BREAK", long: "LONG BREAK" };
const CONTROLS_HIDE_MS = 3000;

async function boot(): Promise<void> {
  const api = await connect();
  const state = await api.get_state();
  let settings: Settings = state.settings;
  let task = "";
  let sessionId: number | null = null;

  // --- DOM -------------------------------------------------------------
  const app = document.getElementById("app")!;
  const frame = document.createElement("div");
  frame.id = "frame";
  const scene = new Scene();
  const clock = new FlipClock();
  const center = document.createElement("div");
  center.className = "center";
  const label = document.createElement("div");
  label.className = "label";
  center.append(clock.el, label);

  const controls = document.createElement("div");
  controls.className = "controls";
  const buttons: [string, string, string, () => void][] = [
    ["play", "Start / pause", "Space", () => timer.toggle()],
    ["reset", "Reset", "R", () => timer.reset()],
    ["skip", "Skip phase", "N", () => timer.skip()],
    ["task", "Set task", "T", () => taskPanel.openWith(task)],
    ["settings", "Settings", "S", () => settingsPanel.openWith(settings)],
    ["full", "Full screen", "F", () => void api.toggle_fullscreen()],
  ];
  // Android is always immersive full screen, so there is nothing to toggle.
  if (isNative()) buttons.pop();
  const buttonEls: Record<string, HTMLButtonElement> = {};
  for (const [id, title, key, action] of buttons) {
    const b = document.createElement("button");
    b.className = `ctl ctl-${id}`;
    b.title = `${title} (${key})`;
    b.innerHTML = `<span class="ctl-label">${title}</span><kbd>${key}</kbd>`;
    b.addEventListener("click", () => {
      action();
      b.blur();
    });
    controls.append(b);
    buttonEls[id] = b;
  }

  const taskPanel = new TaskPanel((t) => {
    task = t;
    renderLabel();
  });
  const backgrounds = state.assets.filter((a) => a.kind === "background") as Asset<BackgroundMeta>[];
  const allSprites = state.assets.filter((a) => a.kind === "sprite" && a.active) as Asset<SpriteMeta>[];
  const sprites = allSprites.filter((s) => !s.meta.base); // variants are reached through their base
  const shavenOf = (id: string) => allSprites.find((s) => s.meta.base === id && s.meta.mustache === false);
  const chosenSprite = (id: string) => {
    const base = sprites.find((s) => s.id === id) ?? sprites[0];
    return base && !settings.mustache ? (shavenOf(base.id) ?? base) : base;
  };
  const settingsPanel = new SettingsPanel(
    (values) => {
      settings = { ...settings, ...values };
      applySettings();
      if (values.background) {
        const picked = backgrounds.find((b) => b.id === values.background);
        if (picked) void scene.setBackground(picked);
      }
      if (values.sprite !== undefined || values.mustache !== undefined) {
        const picked = chosenSprite(settings.sprite);
        if (picked) void scene.setSprites([picked]);
      }
      void api.save_settings(values);
    },
    backgrounds,
    sprites.map((s) => ({
      id: s.id,
      name: s.name,
      src: s.src,
      shavenSrc: shavenOf(s.id)?.src,
      frameWidth: s.meta.frameWidth,
      frameHeight: s.meta.frameHeight,
    })),
  );

  frame.append(scene.canvas, center, controls, taskPanel.el, settingsPanel.el);
  app.append(frame);

  // --- timer -----------------------------------------------------------
  const timerConfig = () => ({
    workMinutes: settings.workMinutes,
    shortMinutes: settings.shortMinutes,
    longMinutes: settings.longMinutes,
    longEvery: settings.longEvery,
    autoStartBreaks: settings.autoStartBreaks,
    autoStartWork: settings.autoStartWork,
  });
  // performance.now() stops while an Android phone sleeps; wall-clock time keeps the deadline honest.
  const timer = new PomodoroTimer(timerConfig(), isNative() ? () => Date.now() : undefined);
  const android = await AndroidShell.setup({
    timer,
    soundOn: () => settings.sound,
    closePanel: () => {
      const wasOpen = taskPanel.isOpen || settingsPanel.isOpen;
      taskPanel.close();
      settingsPanel.close();
      return wasOpen;
    },
  });
  // Skip the in-app chime if the phase-end notification already played it while the app was hidden.
  const playChime = (kind: "work" | "break") => {
    if (settings.sound && !android?.chimeAlreadyPlayed()) chime(kind);
  };

  // Only work phases are logged; that is the time spent on a task.
  timer.on(async (e) => {
    if (e.phase !== "work") {
      if (e.type === "complete") playChime("work");
      return;
    }
    if (e.type === "start") {
      sessionId = await api.start_session(task || null, "work");
    } else if (sessionId !== null) {
      const id = sessionId;
      sessionId = null;
      await api.end_session(id, Math.round(e.elapsedMs / 1000), e.type === "complete");
    }
    if (e.type === "complete") playChime("break");
  });

  function renderLabel(): void {
    const phase = PHASE_LABEL[timer.phase];
    const status = timer.status === "paused" ? " · PAUSED" : timer.status === "idle" ? " · READY" : "";
    label.textContent = task ? `${phase}${status} — ${task}` : `${phase}${status}`;
    label.dataset.phase = timer.phase;
    buttonEls.play.querySelector(".ctl-label")!.textContent = timer.status === "running" ? "Pause" : "Start";
  }

  function applySettings(): void {
    frame.style.setProperty("--frame-color", settings.frameColor);
    frame.style.setProperty("--frame-width", `${settings.frameWidth}px`);
    timer.configure(timerConfig());
  }

  // --- scene assets ----------------------------------------------------
  const bg = backgrounds.find((b) => b.id === settings.background) ?? backgrounds[0];
  if (bg) await scene.setBackground(bg);
  const sprite = chosenSprite(settings.sprite);
  await scene.setSprites(sprite ? [sprite] : []);

  applySettings();

  // --- input -----------------------------------------------------------
  let hideTimer = 0;
  function showControls(): void {
    frame.classList.remove("idle");
    clearTimeout(hideTimer);
    hideTimer = window.setTimeout(() => frame.classList.add("idle"), CONTROLS_HIDE_MS);
  }
  window.addEventListener("mousemove", showControls);
  window.addEventListener("pointerdown", showControls); // touch screens never send mousemove
  showControls();

  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      taskPanel.close();
      settingsPanel.close();
      return;
    }
    if (taskPanel.isOpen || settingsPanel.isOpen) return;
    const actions: Record<string, () => void> = {
      " ": () => timer.toggle(),
      r: () => timer.reset(),
      n: () => timer.skip(),
      t: () => taskPanel.openWith(task),
      s: () => settingsPanel.openWith(settings),
      f: () => void api.toggle_fullscreen(),
    };
    const action = actions[e.key.toLowerCase()];
    if (action) {
      e.preventDefault();
      action();
    }
  });

  // --- main loop -------------------------------------------------------
  // The scene advances by real elapsed time in fixed sub-steps, so a slow renderer
  // makes motion choppier but never slower. Only gaps over MAX_FRAME_S (a hidden or
  // sleeping window) are clamped, so sprites don't teleport on wake.
  const SIM_STEP_S = 1 / 30;
  const MAX_FRAME_S = 0.5;
  let last = performance.now();
  function frameLoop(now: number): void {
    let dt = Math.min(MAX_FRAME_S, Math.max(0, (now - last) / 1000));
    last = now;
    timer.tick();
    clock.show(timer.remainingMs());
    renderLabel();
    while (dt > 0) {
      const step = Math.min(SIM_STEP_S, dt);
      scene.update(step);
      dt -= step;
    }
    scene.draw();
    android?.sync();
    requestAnimationFrame(frameLoop);
  }
  requestAnimationFrame(frameLoop);
}

void boot();
