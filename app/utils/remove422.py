from typing import Set, Any, Callable

from fastapi import FastAPI
from fastapi.routing import APIRoute


def no422(func):
    """
    Tag to remove 422 response from the API docs (because sometimes it just doesn't make sense)
    """
    func.__remove_422__ = True
    return func


def remove_422s(app: FastAPI) -> Callable[[], dict[str, Any]]:
    """
    Create a replacement openapi function that handles @no422 tags and replaces the HTTPValidationError response content
    """
    old_openapi = app.openapi

    def decorator():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = old_openapi()
        paths_to_update: Set[str] = set()
        for route in app.routes:
            if not isinstance(route, APIRoute):
                continue
            methods = route.methods or ["GET"]
            if getattr(route.endpoint, "__remove_422__", None):
                for method in methods:
                    paths_to_update.add(route.path)
        paths = openapi_schema["paths"]
        for path, operations in paths.items():
            for method, data in operations.items():
                if path in paths_to_update:
                    data["responses"].pop("422", None)

        validation_error = openapi_schema["components"]["schemas"].get("HTTPValidationError")
        if validation_error:
            validation_error["properties"] = {"detail": {"title": "Detail", "type": "string"}}
            validation_error["required"] = ["detail"]
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return decorator
