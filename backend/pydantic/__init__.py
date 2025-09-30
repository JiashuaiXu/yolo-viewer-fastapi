from __future__ import annotations

from typing import Any, Dict


class BaseModel:
    """Lightweight stand-in for pydantic.BaseModel used in tests."""

    def __init__(self, **data: Any) -> None:
        annotations = getattr(self.__class__, "__annotations__", {})
        for key in annotations:
            value = data.pop(key, None)
            setattr(self, key, value)
        for key, value in data.items():
            setattr(self, key, value)

    def dict(self) -> Dict[str, Any]:
        return {key: self._serialise(getattr(self, key)) for key in self.__annotations__}

    def model_dump(self) -> Dict[str, Any]:
        return self.dict()

    def _serialise(self, value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value.dict()
        if isinstance(value, list):
            return [self._serialise(item) for item in value]
        if isinstance(value, tuple):
            return tuple(self._serialise(item) for item in value)
        if isinstance(value, dict):
            return {key: self._serialise(item) for key, item in value.items()}
        return value

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        fields = ", ".join(f"{name}={getattr(self, name)!r}" for name in self.__annotations__)
        return f"{self.__class__.__name__}({fields})"


__all__ = ["BaseModel"]
