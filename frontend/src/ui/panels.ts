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

/** A sprite sheet; the thumbnail shows its first frame (standing, facing the viewer). */
export interface SpriteChoice {
  id: string;
  name: string;
  src: string;
  /** Clean-shaven sheet, when the sprite has a mustache to remove. */
  shavenSrc?: string;
  frameWidth: number;
  frameHeight: number;
}

/** A row of pixel thumbnails with the selected item's name in the heading. */
class Picker {
  readonly head: HTMLDivElement;
  readonly grid: HTMLDivElement;
  private name: HTMLSpanElement;
  private buttons = new Map<string, HTMLButtonElement>();

  constructor(
    label: string,
    private choices: { id: string; name: string }[],
    gridClass: string,
    thumb: (choice: { id: string; name: string }) => HTMLElement,
    onPick: (id: string) => void,
  ) {
    this.head = el("div", "bg-head", `${label}: `);
    this.name = el("span", "bg-name");
    this.head.append(this.name);
    this.grid = el("div", gridClass);
    for (const choice of choices) {
      const b = el("button", "bg-thumb");
      b.type = "button";
      b.title = choice.name;
      b.append(thumb(choice));
      b.addEventListener("click", () => {
        this.select(choice.id);
        onPick(choice.id);
      });
      this.grid.append(b);
      this.buttons.set(choice.id, b);
    }
  }

  select(id: string): void {
    for (const [choiceId, b] of this.buttons) b.classList.toggle("selected", choiceId === id);
    this.name.textContent = this.choices.find((c) => c.id === id)?.name ?? "";
  }
}

type NumberKey = "frameWidth" | "workMinutes" | "shortMinutes" | "longMinutes" | "longEvery";
type BoolKey = "autoStartBreaks" | "autoStartWork" | "sound" | "mustache";

export class SettingsPanel extends Panel {
  private inputs = new Map<keyof Settings, HTMLInputElement>();

  private bgPicker: Picker;
  private spritePicker: Picker;
  private spriteThumbs = new Map<SpriteChoice, HTMLElement>();

  /** onChange fires live on every edit so the border, background and sprite preview instantly. */
  constructor(
    private onChange: (values: Partial<Settings>) => void,
    backgrounds: BackgroundChoice[] = [],
    sprites: SpriteChoice[] = [],
  ) {
    super("Settings");

    // Background picker: pixel thumbnails, tap to switch.
    this.bgPicker = new Picker("Background", backgrounds, "bg-grid", (choice) => {
      const img = el("img");
      img.src = (choice as BackgroundChoice).src;
      img.alt = choice.name;
      return img;
    }, (id) => this.onChange({ background: id }));
    if (backgrounds.length > 1) this.body.append(this.bgPicker.head, this.bgPicker.grid);

    // Sprite picker: the first frame of each sheet, scaled up crisply.
    this.spritePicker = new Picker("Sprite", sprites, "sprite-grid", (choice) => {
      const { src, frameWidth, frameHeight } = choice as SpriteChoice;
      const face = el("div", "sprite-thumb");
      face.style.backgroundImage = `url("${src}")`;
      this.spriteThumbs.set(choice as SpriteChoice, face);
      face.style.setProperty("--fw", String(frameWidth));
      face.style.setProperty("--fh", String(frameHeight));
      face.setAttribute("role", "img");
      face.setAttribute("aria-label", choice.name);
      return face;
    }, (id) => this.onChange({ sprite: id }));
    if (sprites.length > 1) this.body.append(this.spritePicker.head, this.spritePicker.grid);
    if (sprites.some((s) => s.shavenSrc)) {
      const row = el("div", "settings-grid sprite-options");
      const mustache = this.field(row, "mustache", "Mustache", "checkbox");
      mustache.addEventListener("change", () => {
        this.showMustache(mustache.checked);
        this.onChange({ mustache: mustache.checked });
      });
      this.body.append(row);
    }

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

  /** Point each sprite thumbnail at its mustache or clean-shaven sheet. */
  private showMustache(on: boolean): void {
    for (const [choice, face] of this.spriteThumbs) {
      face.style.backgroundImage = `url("${on || !choice.shavenSrc ? choice.src : choice.shavenSrc}")`;
    }
  }

  openWith(settings: Settings): void {
    this.bgPicker.select(settings.background);
    this.spritePicker.select(settings.sprite);
    this.showMustache(settings.mustache);
    for (const [key, input] of this.inputs) {
      const v = settings[key];
      if (input.type === "checkbox") input.checked = Boolean(v);
      else input.value = String(v);
    }
    this.open();
  }
}
