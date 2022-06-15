from typing import Optional, Any

from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware


class StatusResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        content = {'status': self.status_code} | content
        return super().render(content)


class ErrorResponse(StatusResponse):
    def __init__(self, message: str, status_code: int, content: Optional[dict] = None):
        if content is None:
            content = {}
        super().__init__(content | {'details': message}, status_code=status_code)


