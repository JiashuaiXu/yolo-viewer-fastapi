import { describe, expect, it } from "vitest";

import { normalizedToPixels } from "./bbox";

describe("normalizedToPixels", () => {
  it("converts normalized box to pixel coordinates", () => {
    const box = normalizedToPixels(
      { cx: 0.5, cy: 0.5, width: 0.25, height: 0.5 },
      { width: 800, height: 400 }
    );

    expect(box.left).toBeCloseTo(300);
    expect(box.top).toBeCloseTo(100);
    expect(box.width).toBeCloseTo(200);
    expect(box.height).toBeCloseTo(200);
  });

  it("handles boxes at the origin", () => {
    const box = normalizedToPixels(
      { cx: 0, cy: 0, width: 0.1, height: 0.1 },
      { width: 1000, height: 500 }
    );

    expect(box.left).toBeCloseTo(-50);
    expect(box.top).toBeCloseTo(-25);
  });
});
