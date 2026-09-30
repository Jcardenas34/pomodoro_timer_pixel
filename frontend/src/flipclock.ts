/**
 * Split-flap MM:SS display, like an old railway departure board.
 *
 * Each card has static top/bottom halves plus, while flipping, two flaps:
 * the top flap (old digit) folds down to 90°, then the bottom flap (new digit)
 * folds from 90° down flat. Only cards whose digit changed animate.
 */

const FLIP_MS = 300;

function half(pos: "top" | "bottom", digit: string, extra = ""): HTMLDivElement {
  const el = document.createElement("div");
  el.className = `half ${pos} ${extra}`.trim();
  const span = document.createElement("span");
  span.textContent = digit;
  el.appendChild(span);
  return el;
}

class FlipCard {
  readonly el: HTMLDivElement;
  private value = "";
  private top: HTMLDivElement;
  private bottom: HTMLDivElement;

  constructor() {
    this.el = document.createElement("div");
    this.el.className = "card";
    this.top = half("top", "0");
    this.bottom = half("bottom", "0");
    this.el.append(this.top, this.bottom);
  }

  set(digit: string, animate: boolean): void {
    if (digit === this.value) return;
    const prev = this.value || digit;
    this.value = digit;
    this.setText(this.top, digit);
    if (!animate || prev === digit) {
      this.setText(this.bottom, digit);
      return;
    }
    // Clear any flip still in progress so rapid changes don't pile up.
    this.el.querySelectorAll(".flap").forEach((f) => f.remove());
    this.setText(this.bottom, prev);
    const flapTop = half("top", prev, "flap flap-top");
    const flapBottom = half("bottom", digit, "flap flap-bottom");
    this.el.append(flapTop, flapBottom);
    flapBottom.addEventListener("animationend", () => {
      this.setText(this.bottom, this.value);
      flapTop.remove();
      flapBottom.remove();
    });
  }

  private setText(h: HTMLDivElement, digit: string): void {
    h.firstElementChild!.textContent = digit;
  }
}

export class FlipClock {
  readonly el: HTMLDivElement;
  private cards: FlipCard[];
  private first = true;

  constructor() {
    this.el = document.createElement("div");
    this.el.className = "flipclock";
    this.el.style.setProperty("--flip-ms", `${FLIP_MS}ms`);
    this.cards = [new FlipCard(), new FlipCard(), new FlipCard(), new FlipCard()];
    const colon = document.createElement("div");
    colon.className = "colon";
    colon.innerHTML = "<i></i><i></i>";
    this.el.append(this.cards[0].el, this.cards[1].el, colon, this.cards[2].el, this.cards[3].el);
  }

  /** Show a duration; seconds are rounded up so 0:00 appears only at the end. */
  show(ms: number): void {
    const total = Math.ceil(ms / 1000);
    const mm = Math.min(99, Math.floor(total / 60));
    const ss = total % 60;
    const digits = `${String(mm).padStart(2, "0")}${String(ss).padStart(2, "0")}`;
    digits.split("").forEach((d, i) => this.cards[i].set(d, !this.first));
    this.first = false;
  }
}
