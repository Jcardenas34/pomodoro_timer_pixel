import "@fontsource/oswald/700.css";
import "@fontsource/press-start-2p/400.css";
import "./styles.css";

import { connect, type Asset, type BackgroundMeta, type Settings, type SpriteMeta } from "./bridge";
import { FlipClock } from "./flipclock";
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
  const settingsPanel = new SettingsPanel((values) => {
    settings = { ...settings, ...values };
    applySettings();
    void api.save_settings(values);
  });

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
  const timer = new PomodoroTimer(timerConfig());

  // Only work phases are logged; that is the time spent on a task.
  timer.on(async (e) => {
    if (e.phase !== "work") {
      if (e.type === "complete" && settings.sound) chime("work");
      return;
    }
    if (e.type === "start") {
      sessionId = await api.start_session(task || null, "work");
    } else if (sessionId !== null) {
      const id = sessionId;
      sessionId = null;
      await api.end_session(id, Math.round(e.elapsedMs / 1000), e.type === "complete");
    }
    if (e.type === "complete" && settings.sound) chime("break");
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
  const backgrounds = state.assets.filter((a) => a.kind === "background") as Asset<BackgroundMeta>[];
  const sprites = state.assets.filter((a) => a.kind === "sprite" && a.active) as Asset<SpriteMeta>[];
  const bg = backgrounds.find((b) => b.id === settings.background) ?? backgrounds[0];
  if (bg) await scene.setBackground(bg);
  await scene.setSprites(sprites);

  applySettings();

  // --- input -----------------------------------------------------------
  let hideTimer = 0;
  function showControls(): void {
    frame.classList.remove("idle");
    clearTimeout(hideTimer);
    hideTimer = window.setTimeout(() => frame.classList.add("idle"), CONTROLS_HIDE_MS);
  }
  window.addEventListener("mousemove", showControls);
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
  let last = performance.now();
  function frameLoop(now: number): void {
    const dt = Math.min(0.1, (now - last) / 1000);
    last = now;
    timer.tick();
    clock.show(timer.remainingMs());
    renderLabel();
    scene.update(dt);
    scene.draw();
    requestAnimationFrame(frameLoop);
  }
  requestAnimationFrame(frameLoop);
}

void boot();
