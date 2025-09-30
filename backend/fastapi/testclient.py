from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI


@dataclass
class _Response:
    status_code: int
    _payload: Any

    def json(self) -> Any:
        if isinstance(self._payload, bytes):
            raise ValueError("Binary responses do not support JSON decoding")
        return self._payload

    @property
    def content(self) -> Any:
        return self._payload


class TestClient:
    """Extremely small subset of TestClient suitable for unit tests."""

    def __init__(self, app: FastAPI) -> None:
        self.app = app
        self.app._run_startup()

    def get(self, path: str) -> _Response:
        status, payload = self.app._handle_request("GET", path)
        return _Response(status_code=status, _payload=payload)


__all__ = ["TestClient"]
