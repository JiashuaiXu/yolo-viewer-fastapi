from __future__ import annotations

from pathlib import Path
from typing import Union


class FileResponse:
    """Simple wrapper representing a file response."""

    def __init__(self, path: Union[str, Path]) -> None:
        self.path = Path(path)

    def read_bytes(self) -> bytes:
        return self.path.read_bytes()


__all__ = ["FileResponse"]
