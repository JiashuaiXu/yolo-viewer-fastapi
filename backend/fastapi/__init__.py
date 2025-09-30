from __future__ import annotations

import asyncio
import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


class HTTPException(Exception):
    """Minimal HTTP exception compatible with FastAPI's interface."""

    def __init__(self, status_code: int, detail: Any) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)

    def __str__(self) -> str:  # pragma: no cover - inherited repr is fine
        return str(self.detail)


@dataclass
class _Route:
    method: str
    path: str
    handler: Callable[..., Any]
    response_model: Any = None

    def match(self, method: str, path: str) -> Optional[Dict[str, str]]:
        if method != self.method:
            return None
        target_segments = self._split_path(self.path)
        request_segments = self._split_path(path)
        if len(target_segments) != len(request_segments):
            return None
        params: Dict[str, str] = {}
        for expected, actual in zip(target_segments, request_segments):
            if expected.startswith("{") and expected.endswith("}"):
                params[expected[1:-1]] = actual
            elif expected != actual:
                return None
        return params

    @staticmethod
    def _split_path(path: str) -> List[str]:
        trimmed = path.strip("/")
        if not trimmed:
            return []
        return trimmed.split("/")


class FastAPI:
    """A tiny subset of the FastAPI API surface for testing."""

    def __init__(self, *, title: str = "", version: str = "") -> None:
        self.title = title
        self.version = version
        self._routes: List[_Route] = []
        self._startup_handlers: List[Callable[[], Any]] = []

    def add_middleware(self, *args: Any, **kwargs: Any) -> None:
        """Middleware is ignored in the test stub."""

    def on_event(self, event_type: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        if event_type != "startup":
            raise ValueError("Only the 'startup' event is supported in the test stub.")

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self._startup_handlers.append(func)
            return func

        return decorator

    def get(self, path: str, response_model: Any = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self._routes.append(_Route(method="GET", path=path, handler=func, response_model=response_model))
            return func

        return decorator

    def _find_route(self, method: str, path: str) -> Optional[Dict[str, Any]]:
        for route in self._routes:
            params = route.match(method, path)
            if params is not None:
                return {"route": route, "params": params}
        return None

    def _serialise(self, value: Any) -> Any:
        from fastapi.responses import FileResponse  # Local import to avoid cycle

        if hasattr(value, "model_dump") and callable(value.model_dump):
            return value.model_dump()
        if hasattr(value, "dict") and callable(value.dict):  # pragma: no cover - fallback
            return value.dict()
        if isinstance(value, list):
            return [self._serialise(item) for item in value]
        if isinstance(value, dict):
            return {key: self._serialise(item) for key, item in value.items()}
        if isinstance(value, FileResponse):
            return value.read_bytes()
        return value

    def _run_startup(self) -> None:
        for handler in self._startup_handlers:
            if inspect.iscoroutinefunction(handler):
                asyncio.run(handler())
            else:
                handler()

    def _handle_request(self, method: str, path: str) -> tuple[int, Any]:
        match = self._find_route(method, path)
        if match is None:
            return 404, {"detail": "Not Found"}
        route: _Route = match["route"]
        params: Dict[str, str] = match["params"]
        try:
            result = route.handler(**params)
            status = 200
        except HTTPException as exc:
            return exc.status_code, {"detail": exc.detail}
        if inspect.isawaitable(result):
            result = asyncio.run(result)
        return status, self._serialise(result)


__all__ = ["FastAPI", "HTTPException"]
