// Captures the README screenshots from the browser-only build (src/local.ts backend).
//
//   cd backend && python -m pomodoro --export-demo ../frontend/public/demo
//   cd ../frontend && npm run build && npm run screenshots
//
// Writes PNGs to docs/screenshots/ and raw GIF frames to docs/screenshots/.frames/,
// which scripts/make-hero-gif.py turns into hero.gif.
import { spawn } from "node:child_process";
import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const FRONTEND = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const OUT = resolve(FRONTEND, "../docs/screenshots");
const FRAMES = join(OUT, ".frames");
const PORT = 4179;
const URL = `http://localhost:${PORT}/`;
const TASK = "Polish the README";
const HERO_CITIES = ["fuji", "london", "uppsala", "paris"];
const HERO_SECONDS_PER_CITY = 3;
const HERO_FPS = 12;

const manifest = JSON.parse(await readFile(join(FRONTEND, "dist/demo/manifest.json"), "utf8"));
const backgrounds = manifest.filter((a) => a.kind === "background");
const nameOf = (city) => backgrounds.find((b) => b.id === `builtin:${city}`).name;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function startServer() {
  const proc = spawn("npx", ["vite", "preview", "--port", String(PORT), "--strictPort"], {
    cwd: FRONTEND,
    stdio: "ignore",
  });
  for (let i = 0; i < 60; i++) {
    try {
      if ((await fetch(URL)).ok) return proc;
    } catch {
      /* not up yet */
    }
    await sleep(250);
  }
  proc.kill();
  throw new Error("vite preview did not start");
}

/** Opens the app with `settings` seeded into the local backend's store. */
async function openApp(context, settings = {}) {
  await context.addInitScript((s) => {
    if (!sessionStorage.getItem("seeded")) {
      localStorage.setItem("settings", JSON.stringify(s));
      sessionStorage.setItem("seeded", "1");
    }
  }, settings);
  const page = await context.newPage();
  await page.goto(URL);
  await page.waitForSelector("#frame canvas");
  await page.evaluate(() => document.fonts.ready);
  await sleep(800); // first sprite steps + effect particles
  return page;
}

async function setTask(page, task) {
  await page.keyboard.press("t");
  await page.keyboard.type(task);
  await page.keyboard.press("Enter");
}

async function pickBackground(page, city) {
  await page.keyboard.press("s");
  await page.click(`.bg-thumb[title="${nameOf(city)}"]`);
  await page.keyboard.press("Escape");
}

/** Waits for the control bar to auto-hide so the shot is clean. */
async function waitIdle(page) {
  await page.waitForSelector("#frame.idle", { timeout: 10_000 });
  await sleep(400); // fade-out transition
}

const server = await startServer();
const browser = await chromium.launch();
try {
  await rm(FRAMES, { recursive: true, force: true });
  await mkdir(FRAMES, { recursive: true });

  // --- desktop gallery: one still per scene ------------------------------
  const desktop = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  const page = await openApp(desktop);
  await setTask(page, TASK);
  await page.keyboard.press(" ");
  await sleep(2500); // let the clock tick off a couple of seconds
  for (const bg of backgrounds) {
    const city = bg.id.replace("builtin:", "");
    await pickBackground(page, city);
    await page.mouse.move(5, 5);
    await waitIdle(page);
    await page.screenshot({ path: join(OUT, `scene-${city}.png`) });
    console.log("scene", city);
  }

  // Settings panel over London.
  await pickBackground(page, "london");
  await page.keyboard.press("s");
  await sleep(300);
  await page.screenshot({ path: join(OUT, "settings.png") });
  await page.keyboard.press("Escape");

  // Controls visible.
  await pickBackground(page, "fuji");
  await page.mouse.move(640, 400);
  await sleep(300);
  await page.screenshot({ path: join(OUT, "controls.png") });
  await desktop.close();

  // --- hero GIF frames: cycle cities while the clock runs ----------------
  const hero = await browser.newContext({ viewport: { width: 960, height: 540 } });
  const hp = await openApp(hero);
  await setTask(hp, TASK);
  await hp.keyboard.press(" ");
  await hp.mouse.move(5, 5);
  const frames = [];
  for (const city of HERO_CITIES) {
    await pickBackground(hp, city);
    await waitIdle(hp);
    const end = Date.now() + HERO_SECONDS_PER_CITY * 1000;
    while (Date.now() < end) {
      const t0 = Date.now();
      const file = `f${String(frames.length).padStart(4, "0")}.png`;
      await hp.screenshot({ path: join(FRAMES, file) });
      const wait = 1000 / HERO_FPS - (Date.now() - t0);
      if (wait > 0) await sleep(wait);
      frames.push({ file, ms: Date.now() - t0 });
    }
    console.log("hero", city, frames.length);
  }
  await writeFile(join(FRAMES, "frames.json"), JSON.stringify(frames));
  await hero.close();

  // --- phone: Android-sized landscape with tap controls shown ------------
  const phone = await browser.newContext({
    viewport: { width: 915, height: 412 },
    deviceScaleFactor: 2,
    isMobile: true,
    hasTouch: true,
  });
  const pp = await openApp(phone, { background: "builtin:la" });
  await setTask(pp, TASK);
  await pp.keyboard.press(" ");
  // The APK is always immersive, so it has no full-screen button.
  await pp.evaluate(() => document.querySelector(".ctl-full")?.remove());
  await sleep(2500);
  await pp.touchscreen.tap(457, 120);
  await sleep(300);
  await pp.screenshot({ path: join(OUT, "phone.png") });
  await phone.close();
} finally {
  await browser.close();
  server.kill();
}
