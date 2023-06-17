from abc import ABC, abstractmethod
from typing import Any, Callable

from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.routing import BaseRoute

from app.openapi.no422 import is_marked_no422
from app.openapi.strings import Tag


class OpenApiResolver(ABC):
    """Base class for classes that can generate an OpenAPI specification"""

    @abstractmethod
    def get_schema(self) -> dict[str, Any]:
        pass


class BaseResolver(OpenApiResolver):
    """Class that turns a mapper function into a resolver"""

    MapperFunction = Callable[[], dict[str, Any]]

    def __init__(self, mapper_function: MapperFunction):
        self.mapper_function = mapper_function

    def get_schema(self) -> dict[str, Any]:
        return self.mapper_function()


class CachingDecorator(OpenApiResolver):
    """Decorator that caches the generated specification so that it's not remade on every page load"""

    def __init__(self, app: FastAPI, resolver: OpenApiResolver):
        self.app = app
        self.resolver = resolver

    def get_schema(self) -> dict[str, Any]:
        if not self.app.openapi_schema:
            self.app.openapi_schema = self.resolver.get_schema()
        return self.app.openapi_schema


class Remove422Decorator(OpenApiResolver):
    """Decorator that removes '422' from the list of responses for @no422 tagged routes"""

    def __init__(self, routes: list[BaseRoute], resolver: OpenApiResolver):
        self.routes = routes
        self.resolver = resolver

    def get_schema(self) -> dict[str, Any]:
        schema = self.resolver.get_schema()
        paths_to_update_by_method: dict[str, list[str]] = {}
        # find API routes tagged with @no422
        for route in self.routes:
            if not isinstance(route, APIRoute):
                continue
            if is_marked_no422(route.endpoint):
                methods = route.methods or ["GET"]
                for method in methods:
                    if method not in paths_to_update_by_method:
                        paths_to_update_by_method[method] = []
                    paths_to_update_by_method[method].append(route.path)

        # remove 422 response from those routes
        paths = schema["paths"]
        for path, operations in paths.items():
            for method, data in operations.items():
                if path in paths_to_update_by_method.get(method.upper(), []):
                    data["responses"].pop("422", None)

        return schema


class ValidationErrorSchemaDecorator(OpenApiResolver):
    """Decorator that inserts a proper schema for the HTTPValidationError (422) response"""

    def __init__(self, resolver: OpenApiResolver):
        self.resolver = resolver

    def get_schema(self) -> dict[str, Any]:
        schema = self.resolver.get_schema()
        validation_error = schema["components"]["schemas"].get("HTTPValidationError")
        if validation_error:
            validation_error["properties"] = {"detail": {"title": "Detail", "type": "string"}}
            validation_error["required"] = ["detail"]
        return schema


class TagGroupsDecorator(OpenApiResolver):
    """Decorator that inserts tag groups into the schema"""

    def __init__(self, groups: dict[str, list[Tag]], resolver: OpenApiResolver):
        self.resolver = resolver
        self.groups = groups

    def get_schema(self) -> dict[str, Any]:
        schema = self.resolver.get_schema()
        groups_schema = []
        for name, group in self.groups.items():
            groups_schema.append({"name": name, "tags": [t.name for t in group]})
        schema["x-tagGroups"] = groups_schema
        return schema


class ApiLogoDecorator(OpenApiResolver):
    """Decorator that inserts a logo into the schema"""

    def __init__(self, url: str, alt_text: str, resolver: OpenApiResolver):
        self.url = url
        self.resolver = resolver
        self.alt_text = alt_text

    def get_schema(self) -> dict[str, Any]:
        schema = self.resolver.get_schema()
        schema["info"]["x-logo"] = {"url": self.url, "altText": self.alt_text}
        return schema
