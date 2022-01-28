import importlib
import pkgutil

import pltflow.styles as defined_styles


def load_styles() -> dict:

    styles = [x.name for x in pkgutil.iter_modules(defined_styles.__path__)]  # type: ignore

    STYLES = {}

    for style in styles:

        STYLES[style] = importlib.import_module(f"pltflow.styles.{style}").style  # type: ignore

    return STYLES
