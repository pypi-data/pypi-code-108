from __future__ import annotations

import ckan.plugins.toolkit as tk
from flask import Blueprint
from flask.views import MethodView

from ckanext.iso19115 import utils

iso19115 = Blueprint("iso19115", __name__)


def get_blueprints():
    return [iso19115]


class ValidateView(MethodView):
    def post(
        self,
    ):
        value = tk.request.form.get("content", "")
        content = bytes(value, "utf8")
        errors = {}

        try:
            utils.validate_schema(content, validate_codelists=True)
            utils.validate_schematron(content)
        except tk.ValidationError as e:
            errors = e.error_summary
            tk.h.flash_error("Document is not valid")
        else:
            tk.h.flash_success("Document is valid")

        return self._render({"content": value}, errors)

    def get(self):
        return self._render()

    def _render(self, data=None, errors=None):
        extra_vars = {"data": data, "errors": errors}

        return tk.render("iso19115/validate.html", extra_vars)


iso19115.add_url_rule(
    "/-iso19115/validate", view_func=ValidateView.as_view("validate")
)
