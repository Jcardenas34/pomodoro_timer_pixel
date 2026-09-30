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
    private ground: BackgroundMeta,
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

/** Cherry-blossom petals drifting down across the scene. */
class Petal {
  x = rand(0, SCENE_W);
  y = rand(-SCENE_H, 0);
  private vy = rand(6, 14);
  private phase = rand(0, Math.PI * 2);
  private color = Math.random() < 0.5 ? "#ffcde1" : "#ff96be";

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

export class Scene {
  readonly canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private bg: HTMLImageElement | null = null;
  private bgMeta: BackgroundMeta = { groundTop: 150, groundBottom: 176 };
  private sprites: Wanderer[] = [];
  private petals: Petal[] = [];
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
    this.petals = asset.meta.petals ? Array.from({ length: 28 }, () => new Petal()) : [];
  }

  async setSprites(assets: Asset<SpriteMeta>[]): Promise<void> {
    const imgs = await Promise.all(assets.map((a) => loadImage(a.src)));
    this.sprites = assets.map((a, i) => new Wanderer(imgs[i], a.meta, this.bgMeta));
  }

  update(dt: number): void {
    this.t += dt;
    for (const s of this.sprites) s.update(dt);
    for (const p of this.petals) p.update(dt, this.t);
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
    for (const p of this.petals) p.draw(ctx);
  }
}
