import type { Asset, BackgroundMeta, Direction, SpriteMeta } from "./bridge";

export const SCENE_W = 320;
export const SCENE_H = 180;
const WALK_SPEED = 20; // scene pixels per second
const GRID = 8; // walk targets snap to this, like overworld tiles

function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
}

const rand = (min: number, max: number) => min + Math.random() * (max - min);

type Facing = Direction | "left";

/**
 * A sprite that strolls around the ground band like an overworld NPC: it walks
 * one axis at a time (never diagonally) toward grid-snapped spots, then stands
 * for a while and sometimes turns to face the viewer.
 */
class Wanderer {
  x: number;
  y: number;
  private targetX: number;
  private targetY: number;
  private idleFor = 0;
  private stepT = 0;
  private facing: Facing = "down";

  constructor(
    private img: HTMLImageElement,
    private meta: SpriteMeta,
    public ground: BackgroundMeta,
  ) {
    this.x = this.snap(rand(24, SCENE_W - 24));
    this.y = this.pickY();
    this.targetX = this.x;
    this.targetY = this.y;
    this.idleFor = rand(0.5, 2);
  }

  private snap(v: number): number {
    return Math.round(v / GRID) * GRID;
  }

  /** Feet y within the walkable band. */
  private pickY(): number {
    const top = this.ground.groundTop + 6;
    return Math.round(rand(top, this.ground.groundBottom));
  }

  /** Move onto a new background's walkable band. */
  setGround(ground: BackgroundMeta): void {
    this.ground = ground;
    if (this.y < ground.groundTop + 6 || this.y > ground.groundBottom) {
      this.y = this.targetY = this.pickY();
    }
  }

  /** Continue from another walker's position, heading and pause (used when swapping sprites). */
  takePlaceOf(other: Wanderer): void {
    this.x = other.x;
    this.y = other.y;
    this.targetX = other.targetX;
    this.targetY = other.targetY;
    this.idleFor = other.idleFor;
    this.stepT = other.stepT;
    this.facing = other.facing;
  }

  update(dt: number): void {
    if (this.idleFor > 0) {
      this.idleFor -= dt;
      // Now and then glance at the viewer, like a waiting NPC.
      if (this.idleFor > 0.5 && Math.random() < dt * 0.4) this.facing = "down";
      if (this.idleFor <= 0) {
        this.targetX = this.snap(rand(16, SCENE_W - 16));
        this.targetY = this.pickY();
        this.stepT = 0;
      }
      return;
    }
    const dx = this.targetX - this.x;
    const dy = this.targetY - this.y;
    const step = WALK_SPEED * dt;
    this.stepT += dt;
    // Finish the horizontal leg first, then the vertical one.
    if (Math.abs(dx) >= 0.5) {
      this.facing = dx > 0 ? "right" : "left";
      this.x += Math.sign(dx) * Math.min(Math.abs(dx), step);
    } else if (Math.abs(dy) >= 0.5) {
      this.x = this.targetX;
      this.facing = dy > 0 ? "down" : "up";
      this.y += Math.sign(dy) * Math.min(Math.abs(dy), step);
    } else {
      this.y = this.targetY;
      this.idleFor = rand(1.5, 5);
    }
  }

  draw(ctx: CanvasRenderingContext2D): void {
    const { frameWidth: fw, frameHeight: fh, fps } = this.meta;
    const dir: Direction = this.facing === "left" ? "right" : this.facing;
    const frame =
      this.idleFor > 0
        ? this.meta.idle[dir]
        : this.meta.walk[dir][Math.floor(this.stepT * fps) % this.meta.walk[dir].length];
    const left = Math.round(this.x - fw / 2);
    const top = Math.round(this.y - fh);
    // Oval drop shadow under the feet.
    ctx.fillStyle = "rgba(0,0,0,0.28)";
    ctx.fillRect(left + 10, top + fh - 2, 12, 1);
    ctx.fillRect(left + 11, top + fh - 1, 10, 1);
    ctx.save();
    if (this.facing === "left") {
      ctx.translate(left + fw, top);
      ctx.scale(-1, 1);
      ctx.drawImage(this.img, frame * fw, 0, fw, fh, 0, 0, fw, fh);
    } else {
      ctx.drawImage(this.img, frame * fw, 0, fw, fh, left, top, fw, fh);
    }
    ctx.restore();
  }
}

interface Particle {
  update(dt: number, t: number): void;
  draw(ctx: CanvasRenderingContext2D): void;
}

const pick = <T,>(xs: T[]): T => xs[Math.floor(Math.random() * xs.length)];

/** Blossoms drifting down and to the right: cherry (Fuji) or jacaranda (LA, CDMX). */
class Petal implements Particle {
  x = rand(0, SCENE_W);
  y = rand(-SCENE_H, 0);
  private vy = rand(6, 14);
  private phase = rand(0, Math.PI * 2);
  private color: string;

  constructor(colors: string[]) {
    this.color = pick(colors);
  }

  update(dt: number, t: number): void {
    this.y += this.vy * dt;
    this.x += (Math.sin(t * 1.5 + this.phase) * 8 + 4) * dt;
    if (this.y > SCENE_H || this.x > SCENE_W + 2) {
      this.x = rand(-20, SCENE_W * 0.6);
      this.y = rand(-20, 0);
    }
  }

  draw(ctx: CanvasRenderingContext2D): void {
    ctx.fillStyle = this.color;
    ctx.fillRect(Math.round(this.x), Math.round(this.y), 1, 1);
  }
}

/** Autumn leaves: slower, wider sway, tumbling between flat and edge-on (Paris, Bologna). */
class Leaf implements Particle {
  x = rand(0, SCENE_W);
  y = rand(-SCENE_H, 0);
  private vy = rand(5, 10);
  private phase = rand(0, Math.PI * 2);
  private color = pick(["#e0a040", "#c86a30", "#a04a2c", "#d8b050"]);
  private flat = true;

  update(dt: number, t: number): void {
    this.y += this.vy * dt;
    this.x += Math.sin(t * 1.1 + this.phase) * 14 * dt;
    this.flat = Math.sin(t * 3 + this.phase) > 0;
    if (this.y > SCENE_H) {
      this.x = rand(0, SCENE_W);
      this.y = rand(-20, 0);
    }
  }

  draw(ctx: CanvasRenderingContext2D): void {
    ctx.fillStyle = this.color;
    ctx.fillRect(Math.round(this.x), Math.round(this.y), this.flat ? 2 : 1, this.flat ? 1 : 2);
  }
}

/** Snowfall in two depths: small slow flakes behind, bigger faster ones in front (Uppsala, Stockholm). */
class Snowflake implements Particle {
  x = rand(0, SCENE_W);
  y = rand(-SCENE_H, SCENE_H);
  private near = Math.random() < 0.3;
  private vy = this.near ? rand(14, 20) : rand(6, 11);
  private phase = rand(0, Math.PI * 2);

  update(dt: number, t: number): void {
    this.y += this.vy * dt;
    this.x += Math.sin(t * 0.8 + this.phase) * 5 * dt;
    if (this.y > SCENE_H) {
      this.x = rand(0, SCENE_W);
      this.y = rand(-10, 0);
    }
  }

  draw(ctx: CanvasRenderingContext2D): void {
    ctx.fillStyle = this.near ? "#ffffff" : "#c8d4f0";
    const size = this.near ? 2 : 1;
    ctx.fillRect(Math.round(this.x), Math.round(this.y), size, size);
  }
}

/** Spray blowing off the top of a fountain, twinkling as it drifts and falls (Geneva). */
class Mist implements Particle {
  private x = 0;
  private y = 0;
  private vx = 0;
  private vy = 0;
  private life = 0;

  constructor(private origin: [number, number]) {
    this.reset();
    this.life = rand(0, 4);
  }

  private reset(): void {
    this.x = this.origin[0] + rand(-2, 2);
    this.y = this.origin[1] + rand(-4, 4);
    this.vx = rand(4, 12);
    this.vy = rand(-2, 3);
    this.life = rand(3, 6);
  }

  update(dt: number): void {
    this.life -= dt;
    this.vy += 4 * dt; // gravity pulls the spray down toward the lake
    this.x += this.vx * dt;
    this.y += this.vy * dt;
    if (this.life <= 0) this.reset();
  }

  draw(ctx: CanvasRenderingContext2D): void {
    ctx.fillStyle = Math.random() < 0.25 ? "#ffffff" : "#c4def6";
    ctx.fillRect(Math.round(this.x), Math.round(this.y), 1, 1);
  }
}

/** Fireflies hovering over the grass, blinking on and off (Arlington). */
class Firefly implements Particle {
  private x = rand(0, SCENE_W);
  private y = rand(118, 158);
  private phase = rand(0, Math.PI * 2);
  private speed = rand(0.6, 1.4);
  private glow = 0;

  update(dt: number, t: number): void {
    this.x += Math.sin(t * this.speed + this.phase) * 6 * dt;
    this.y += Math.cos(t * this.speed * 0.7 + this.phase) * 3 * dt;
    this.glow = Math.max(0, Math.sin(t * 1.6 * this.speed + this.phase * 3));
  }

  draw(ctx: CanvasRenderingContext2D): void {
    if (this.glow < 0.3) return;
    const x = Math.round(this.x);
    const y = Math.round(this.y);
    if (this.glow > 0.8) {
      ctx.fillStyle = "rgba(255, 240, 120, 0.35)";
      ctx.fillRect(x - 1, y, 3, 1);
      ctx.fillRect(x, y - 1, 1, 3);
    }
    ctx.fillStyle = "#fff38a";
    ctx.fillRect(x, y, 1, 1);
  }
}

/** Slanted drizzle with a brief splash where each drop lands on the pavement (London). */
class Raindrop implements Particle {
  x = rand(-20, SCENE_W);
  y = rand(-SCENE_H, SCENE_H);
  private near = Math.random() < 0.35;
  private vy = this.near ? rand(150, 190) : rand(100, 130);
  private landY = rand(158, 178);
  private splash = 0;

  update(dt: number): void {
    if (this.splash > 0) {
      this.splash -= dt;
      if (this.splash <= 0) this.reset();
      return;
    }
    this.y += this.vy * dt;
    this.x += this.vy * 0.25 * dt; // wind from the left
    if (this.y >= this.landY) {
      this.y = this.landY;
      this.splash = 0.12;
    }
  }

  private reset(): void {
    this.x = rand(-40, SCENE_W);
    this.y = rand(-20, 0);
    this.landY = rand(158, 178);
  }

  draw(ctx: CanvasRenderingContext2D): void {
    const x = Math.round(this.x);
    const y = Math.round(this.y);
    if (this.splash > 0) {
      ctx.fillStyle = "rgba(200, 214, 240, 0.7)";
      ctx.fillRect(x - 1, y - 1, 1, 1);
      ctx.fillRect(x + 1, y - 1, 1, 1);
      return;
    }
    ctx.fillStyle = this.near ? "rgba(200, 214, 240, 0.75)" : "rgba(160, 176, 214, 0.5)";
    const len = this.near ? 4 : 3;
    for (let i = 0; i < len; i++) ctx.fillRect(x - Math.floor(i / 4), y - i, 1, 1);
  }
}

/** Particles for a background's `effect` (older Fuji metadata only has `petals: true`). */
export function makeParticles(meta: BackgroundMeta): Particle[] {
  const effect = meta.effect ?? (meta.petals ? "petals" : undefined);
  const n = (count: number, make: () => Particle) => Array.from({ length: count }, make);
  switch (effect) {
    case "petals":
      return n(28, () => new Petal(["#ffcde1", "#ff96be"]));
    case "jacaranda":
      return n(28, () => new Petal(["#c49cec", "#9666cc"]));
    case "leaves":
      return n(18, () => new Leaf());
    case "snow":
      return n(70, () => new Snowflake());
    case "mist":
      return n(40, () => new Mist(meta.effectOrigin ?? [SCENE_W / 2, 24]));
    case "fireflies":
      return n(16, () => new Firefly());
    case "rain":
      return n(90, () => new Raindrop());
    default:
      return [];
  }
}

export class Scene {
  readonly canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private bg: HTMLImageElement | null = null;
  private bgMeta: BackgroundMeta = { groundTop: 150, groundBottom: 176 };
  private sprites: Wanderer[] = [];
  private particles: Particle[] = [];
  private t = 0;

  constructor() {
    this.canvas = document.createElement("canvas");
    this.canvas.className = "scene";
    this.canvas.width = SCENE_W;
    this.canvas.height = SCENE_H;
    this.ctx = this.canvas.getContext("2d")!;
    this.ctx.imageSmoothingEnabled = false;
  }

  async setBackground(asset: Asset<BackgroundMeta>): Promise<void> {
    this.bg = await loadImage(asset.src);
    this.bgMeta = asset.meta;
    this.particles = makeParticles(asset.meta);
    for (const s of this.sprites) s.setGround(asset.meta);
  }

  /** Replace the walking sprites. Walkers already on screen keep their spot and heading. */
  async setSprites(assets: Asset<SpriteMeta>[]): Promise<void> {
    const imgs = await Promise.all(assets.map((a) => loadImage(a.src)));
    const previous = this.sprites;
    this.sprites = assets.map((a, i) => {
      const w = new Wanderer(imgs[i], a.meta, this.bgMeta);
      if (previous[i]) w.takePlaceOf(previous[i]);
      return w;
    });
  }

  update(dt: number): void {
    this.t += dt;
    for (const s of this.sprites) s.update(dt);
    for (const p of this.particles) p.update(dt, this.t);
  }

  draw(): void {
    const ctx = this.ctx;
    if (this.bg) ctx.drawImage(this.bg, 0, 0, SCENE_W, SCENE_H);
    else {
      ctx.fillStyle = "#1d2b53";
      ctx.fillRect(0, 0, SCENE_W, SCENE_H);
    }
    // Depth-sort so sprites lower on screen draw in front.
    for (const s of [...this.sprites].sort((a, b) => a.y - b.y)) s.draw(ctx);
    for (const p of this.particles) p.draw(ctx);
  }
}
