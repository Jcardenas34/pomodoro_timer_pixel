import { describe, expect, it } from "vitest";
import type { BackgroundEffect } from "./bridge";
import { makeParticles, SCENE_H } from "./scene";

const ground = { groundTop: 158, groundBottom: 176 };

describe("makeParticles", () => {
  it("builds particles for every city effect", () => {
    const effects: BackgroundEffect[] = ["petals", "jacaranda", "leaves", "snow", "mist", "fireflies"];
    for (const effect of effects) {
      const ps = makeParticles({ ...ground, effect, effectOrigin: [212, 24] });
      expect(ps.length, effect).toBeGreaterThan(0);
      // A few seconds of simulation must not throw.
      for (let t = 0; t < 5; t += 0.1) for (const p of ps) p.update(0.1, t);
    }
  });

  it("keeps legacy Fuji metadata (petals: true) working", () => {
    expect(makeParticles({ ...ground, petals: true })).toHaveLength(28);
  });

  it("returns nothing for a background without an effect", () => {
    expect(makeParticles(ground)).toEqual([]);
  });

  it("recycles snow back to the top after it falls off screen", () => {
    const [flake] = makeParticles({ ...ground, effect: "snow" }) as unknown as { y: number; update(dt: number, t: number): void }[];
    for (let i = 0; i < 400; i++) flake.update(0.1, i * 0.1);
    expect(flake.y).toBeLessThanOrEqual(SCENE_H);
  });
});
