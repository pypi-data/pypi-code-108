import importlib

import venusian

MACROS = []


def macro(f):
    MACROS.append(f)
    return f


def register_macros(app, path):
    scanner = venusian.Scanner()
    scanner.scan(importlib.import_module(path))

    for macro in MACROS:
        app.template_global(macro.__name__)(macro)
