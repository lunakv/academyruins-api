import os

from starlette.datastructures import Headers
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


class CORSPerPathMiddleware:
    """
    Public routes can be called from any origin, while admin routes are only callable from the frontend
    (FRONTEND_URI). If FRONTEND_URI isn't set, admin routes reject all cross-origin requests.

    Admin requests from any other origin are rejected outright, not just hidden by CORS, since a plain form POST
    doesn't need CORS and would otherwise be sent with any HTTP Basic credentials cached by the browser.
    Requests without an Origin header (e.g. curl) are allowed.
    """

    def __init__(self, app: ASGIApp):
        self.frontend = os.environ.get("FRONTEND_URI", "").rstrip("/")
        self.public = CORSMiddleware(app, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
        self.admin = CORSMiddleware(
            app,
            allow_origins=[self.frontend] if self.frontend else [],
            allow_methods=["GET", "PUT", "POST"],
            allow_headers=["Authorization", "Content-Type"],
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        path = scope.get("path", "")
        if path == "/admin" or path.startswith("/admin/"):
            origin = Headers(scope=scope).get("origin")
            if origin is not None and origin != self.frontend:
                await JSONResponse({"detail": "Origin not allowed"}, status_code=403)(scope, receive, send)
                return
            await self.admin(scope, receive, send)
        else:
            await self.public(scope, receive, send)
