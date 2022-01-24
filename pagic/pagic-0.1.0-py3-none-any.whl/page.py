from typing import Any

from devtools import debug
from flask import render_template, request, url_for
from werkzeug.exceptions import MethodNotAllowed

# from app.flask.lib.view_model import unwrap
# from app.services.json_ld import to_json_ld
# from app.services.opengraph import to_opengraph

PAGES = {}


def fqdn(cls):
    return f"{cls.__module__}.{cls.__name__}"


def page(cls):
    debug(f"@page called for page={cls}")
    Page.__all__pages__[fqdn(cls)] = cls
    return cls


class Page:
    __all__pages__ = {}

    name: str
    label: str
    path: str
    template: str
    layout: str
    parent: Any = None
    args: dict = {}

    def context(self):
        """Override in subclasses."""
        return {}

    def get(self):
        return self.render()

    def post(self):
        """Override in subclasses, if needed."""
        raise MethodNotAllowed()

    def render(self):
        ctx = self.context()
        ctx.update(self.extra_context(ctx))
        content = self.content(ctx)
        ctx["content"] = content
        return render_template(self.layout, **ctx)

    def content(self, ctx):
        return render_template(self.template, **ctx)

    def extra_context(self, ctx):
        d = {}

        if "title" not in ctx:
            d["title"] = self.label

        d["breadcrumbs"] = self.breadcrumbs

        d["json_data"] = {}

        # menus = {
        #     "main": g.nav_data["main"],
        #     "user": g.nav_data["user"],
        # }
        # menus.update(self.menus())
        # d["menus"] = menus
        #
        # if hasattr(self, "view_model") and "model" not in d:
        #     d["model"] = self.view_model

        # if "model" in d:
        #     model = unwrap(d["model"])
        #     d["og_data"] = to_opengraph(model)
        #     d["json_ld"] = to_json_ld(model)

        return d

    def menus(self):
        return {}

    @property
    def breadcrumbs(self):
        breadcrumbs = [
            {"name": self.label, "href": self.url, "current": True},
        ]
        if not self.parent:
            return breadcrumbs

        parent = self.parent()
        while True:
            breadcrumbs += [
                {"name": parent.label, "href": parent.url, "current": False},
            ]
            if not parent.parent:
                break
            parent = parent.parent()

        breadcrumbs.reverse()
        return breadcrumbs

    @property
    def url(self):
        return url_for(f".{self.name}", **self.args)

    @property
    def menu(self):
        return []


class Route:
    def __init__(self, page_class):
        self.page_class = page_class

    def __call__(self, **kwargs):
        page = self.page_class(**kwargs)
        method = request.method
        match method:
            case "GET":
                return page.get()
            case "POST":
                return page.post()
