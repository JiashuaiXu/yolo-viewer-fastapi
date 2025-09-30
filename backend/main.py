from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

DATASET_ROOT = Path(
    os.getenv("YOLO_DATASET_DIR", Path(__file__).resolve().parent.parent / "dataset")
).resolve()
IMAGES_DIR = DATASET_ROOT / "images"
LABELS_DIR = DATASET_ROOT / "labels"
CLASSES_FILE = DATASET_ROOT / "classes.txt"
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


class ClassItem(BaseModel):
    id: int
    name: str


class BoundingBox(BaseModel):
    cx: float
    cy: float
    width: float
    height: float


class LabelItem(BaseModel):
    class_id: int
    class_name: str
    bbox: BoundingBox
    confidence: Optional[float] = None


class ImageItem(BaseModel):
    id: str
    filename: str


def _ensure_dataset_structure() -> None:
    if not DATASET_ROOT.exists():
        raise FileNotFoundError(
            f"Dataset directory '{DATASET_ROOT}' was not found. "
            "Set YOLO_DATASET_DIR or create the default ./dataset folder."
        )
    if not IMAGES_DIR.exists():
        raise FileNotFoundError(f"Images directory '{IMAGES_DIR}' is missing.")
    if not LABELS_DIR.exists():
        raise FileNotFoundError(f"Labels directory '{LABELS_DIR}' is missing.")


def _load_classes() -> Dict[int, str]:
    if not CLASSES_FILE.exists():
        raise FileNotFoundError(f"Classes file '{CLASSES_FILE}' is missing.")

    mapping: Dict[int, str] = {}
    with CLASSES_FILE.open("r", encoding="utf-8") as fh:
        for idx, raw_line in enumerate(fh):
            name = raw_line.strip()
            if not name:
                name = f"class_{idx}"
            mapping[idx] = name

    if not mapping:
        raise ValueError("No classes defined in classes.txt.")

    return mapping


def _iter_images() -> Iterable[ImageItem]:
    if not IMAGES_DIR.exists():
        return []
    for path in sorted(IMAGES_DIR.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
            continue
        yield ImageItem(id=path.stem, filename=path.name)


def _resolve_image_path(image_id: str) -> Path:
    candidates = sorted(IMAGES_DIR.glob(f"{image_id}.*"))
    for candidate in candidates:
        if candidate.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
            return candidate
    raise FileNotFoundError(f"Image '{image_id}' not found in {IMAGES_DIR}.")


def _load_labels(image_id: str, classes: Dict[int, str]) -> List[LabelItem]:
    label_path = LABELS_DIR / f"{image_id}.txt"
    if not label_path.exists():
        raise FileNotFoundError(f"Label file '{label_path}' not found.")

    items: List[LabelItem] = []
    with label_path.open("r", encoding="utf-8") as fh:
        for line_no, raw_line in enumerate(fh, start=1):
            stripped = raw_line.strip()
            if not stripped:
                continue
            parts = stripped.split()
            if len(parts) < 5:
                raise ValueError(
                    f"Invalid label line at {label_path}:{line_no} → '{raw_line.rstrip()}'."
                )
            try:
                class_id = int(parts[0])
                cx, cy, width, height = map(float, parts[1:5])
            except ValueError as exc:
                raise ValueError(
                    f"Invalid numeric values at {label_path}:{line_no} → '{raw_line.rstrip()}'"
                ) from exc

            confidence: Optional[float] = None
            if len(parts) >= 6:
                try:
                    confidence = float(parts[5])
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid confidence at {label_path}:{line_no} → '{raw_line.rstrip()}'"
                    ) from exc

            class_name = classes.get(class_id, f"class_{class_id}")
            items.append(
                LabelItem(
                    class_id=class_id,
                    class_name=class_name,
                    bbox=BoundingBox(cx=cx, cy=cy, width=width, height=height),
                    confidence=confidence,
                )
            )
    return items


app = FastAPI(title="YOLO Viewer API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def validate_dataset() -> None:
    _ensure_dataset_structure()


@app.get("/api/classes", response_model=List[ClassItem])
def list_classes() -> List[ClassItem]:
    classes = _load_classes()
    return [ClassItem(id=idx, name=name) for idx, name in classes.items()]


@app.get("/api/images")
def list_images() -> List[ImageItem]:
    return list(_iter_images())


@app.get("/api/image/{image_id}")
def get_image(image_id: str) -> FileResponse:
    try:
        image_path = _resolve_image_path(image_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(image_path)


@app.get("/api/label/{image_id}", response_model=List[LabelItem])
def get_label(image_id: str) -> List[LabelItem]:
    classes = _load_classes()
    try:
        return _load_labels(image_id, classes)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
