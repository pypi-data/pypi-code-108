"""Main module."""
import importlib

import venusian
from flask import Flask

from pagic.page import Page, Route


class Pagic:
    app: Flask | None

    def __init__(self, app: Flask | None = None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        self.app = app
        if "pagic" in app.extensions:
            raise RuntimeError(
                "This extension is already registered on this Flask app."
            )
        app.extensions["pagic"] = self

        # app.before_request(self.before_request)

    def register_pages(self, path=None):
        self.scan_pages(path)

        for page_cls in Page.__all__pages__.values():
            print(f"Registering pags: {page_cls}")
            self.register_page(page_cls)

    def scan_pages(self, path):
        if not path:
            path = "tests"
        module = importlib.import_module(path)
        scanner = venusian.Scanner()
        scanner.scan(module)

    def register_page(self, cls):
        methods = ["GET", "POST"]

        route = Route(cls)
        if hasattr(cls, "routes"):
            for _route in cls.routes:
                self.app.add_url_rule(_route, cls.name, route, methods=methods)
            return

        if not hasattr(cls, "path"):
            cls.path = cls.name

        self.app.add_url_rule(cls.path, cls.name, route, methods=methods)
