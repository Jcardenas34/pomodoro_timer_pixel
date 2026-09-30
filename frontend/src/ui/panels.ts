import type { Settings } from "../bridge";

function el<K extends keyof HTMLElementTagNameMap>(tag: K, className = "", html = ""): HTMLElementTagNameMap[K] {
  const e = document.createElement(tag);
  if (className) e.className = className;
  if (html) e.innerHTML = html;
  return e;
}

/** A centered modal panel. Only one is open at a time. */
class Panel {
  readonly el: HTMLDivElement;
  protected body: HTMLDivElement;

  constructor(title: string) {
    this.el = el("div", "panel");
    this.el.hidden = true;
    const box = el("div", "panel-box");
    box.append(el("h2", "", title));
    this.body = el("div", "panel-body");
    box.append(this.body);
    this.el.append(box);
    this.el.addEventListener("pointerdown", (e) => {
      if (e.target === this.el) this.close();
    });
  }

  get isOpen(): boolean {
    return !this.el.hidden;
  }

  open(): void {
    this.el.hidden = false;
  }

  close(): void {
    this.el.hidden = true;
  }
}

export class TaskPanel extends Panel {
  private input: HTMLInputElement;

  constructor(onSubmit: (task: string) => void) {
    super("What are you working on?");
    const form = el("form");
    this.input = el("input");
    this.input.type = "text";
    this.input.maxLength = 60;
    this.input.placeholder = "e.g. Write chapter 3";
    this.input.enterKeyHint = "done";
    const hint = el("p", "hint keys-hint", "Enter to save &middot; Esc to cancel");
    const save = el("button", "ctl panel-action", "Save");
    save.type = "submit";
    form.append(this.input, hint, save);
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      onSubmit(this.input.value.trim());
      this.close();
    });
    this.body.append(form);
  }

  openWith(current: string): void {
    this.input.value = current;
    this.open();
    this.input.focus();
    this.input.select();
  }
}

export interface BackgroundChoice {
  id: string;
  name: string;
  src: string;
}

type NumberKey = "frameWidth" | "workMinutes" | "shortMinutes" | "longMinutes" | "longEvery";
type BoolKey = "autoStartBreaks" | "autoStartWork" | "sound";

export class SettingsPanel extends Panel {
  private inputs = new Map<keyof Settings, HTMLInputElement>();

  private thumbs = new Map<string, HTMLButtonElement>();
  private bgName: HTMLSpanElement;

  /** onChange fires live on every edit so the border color and background preview instantly. */
  constructor(
    private onChange: (values: Partial<Settings>) => void,
    private backgrounds: BackgroundChoice[] = [],
  ) {
    super("Settings");

    // Background picker: pixel thumbnails, tap to switch.
    const bgHead = el("div", "bg-head", "Background: ");
    this.bgName = el("span", "bg-name");
    bgHead.append(this.bgName);
    const bgGrid = el("div", "bg-grid");
    for (const bg of backgrounds) {
      const b = el("button", "bg-thumb");
      b.type = "button";
      b.title = bg.name;
      const img = el("img");
      img.src = bg.src;
      img.alt = bg.name;
      b.append(img);
      b.addEventListener("click", () => {
        this.selectBackground(bg.id);
        this.onChange({ background: bg.id });
      });
      bgGrid.append(b);
      this.thumbs.set(bg.id, b);
    }
    if (backgrounds.length > 1) this.body.append(bgHead, bgGrid);

    const grid = el("div", "settings-grid");

    const color = this.field(grid, "frameColor", "Border color", "color");
    color.addEventListener("input", () => this.onChange({ frameColor: color.value }));

    const presets = el("div", "swatches");
    for (const c of ["#000000", "#f4f4f4", "#7e2553", "#1d2b53", "#b8860b", "#2e5e3e"]) {
      const b = el("button", "swatch");
      b.type = "button";
      b.style.background = c;
      b.title = c;
      b.addEventListener("click", () => {
        color.value = c;
        this.onChange({ frameColor: c });
      });
      presets.append(b);
    }
    grid.append(el("span"), presets);

    const numbers: [NumberKey, string, number, number][] = [
      ["frameWidth", "Border width (px)", 0, 40],
      ["workMinutes", "Work (min)", 1, 180],
      ["shortMinutes", "Short break (min)", 1, 60],
      ["longMinutes", "Long break (min)", 1, 120],
      ["longEvery", "Long break every", 2, 12],
    ];
    for (const [key, label, min, max] of numbers) {
      const input = this.field(grid, key, label, "number");
      input.min = String(min);
      input.max = String(max);
      input.addEventListener("change", () => {
        const v = Math.min(max, Math.max(min, Number(input.value) || min));
        input.value = String(v);
        this.onChange({ [key]: v });
      });
    }

    const bools: [BoolKey, string][] = [
      ["autoStartBreaks", "Auto-start breaks"],
      ["autoStartWork", "Auto-start work after a break"],
      ["sound", "Chime at phase end"],
    ];
    for (const [key, label] of bools) {
      const input = this.field(grid, key, label, "checkbox");
      input.addEventListener("change", () => this.onChange({ [key]: input.checked }));
    }

    const done = el("button", "ctl panel-action", "Done");
    done.type = "button";
    done.addEventListener("click", () => this.close());
    this.body.append(grid, el("p", "hint", "Changes save automatically<span class=\"keys-hint\"> &middot; Esc to close</span>"), done);
  }

  private field(grid: HTMLElement, key: keyof Settings, label: string, type: string): HTMLInputElement {
    const id = `setting-${key}`;
    const lab = el("label", "", label);
    lab.htmlFor = id;
    const input = el("input");
    input.type = type;
    input.id = id;
    grid.append(lab, input);
    this.inputs.set(key, input);
    return input;
  }

  private selectBackground(id: string): void {
    for (const [bgId, b] of this.thumbs) b.classList.toggle("selected", bgId === id);
    this.bgName.textContent = this.backgrounds.find((bg) => bg.id === id)?.name ?? "";
  }

  openWith(settings: Settings): void {
    this.selectBackground(settings.background);
    for (const [key, input] of this.inputs) {
      const v = settings[key];
      if (input.type === "checkbox") input.checked = Boolean(v);
      else input.value = String(v);
    }
    this.open();
  }
}
