export type NormalizedBox = {
  cx: number;
  cy: number;
  width: number;
  height: number;
};

export type Dimensions = {
  width: number;
  height: number;
};

export type PixelBox = {
  left: number;
  top: number;
  width: number;
  height: number;
};

export function normalizedToPixels(box: NormalizedBox, dims: Dimensions): PixelBox {
  const actualWidth = box.width * dims.width;
  const actualHeight = box.height * dims.height;
  const left = box.cx * dims.width - actualWidth / 2;
  const top = box.cy * dims.height - actualHeight / 2;

  return {
    left,
    top,
    width: actualWidth,
    height: actualHeight
  };
}
