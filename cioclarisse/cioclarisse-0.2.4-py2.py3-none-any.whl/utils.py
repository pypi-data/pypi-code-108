"""
Contexts for performing long or delicate functions.
"""
import os
import re
from contextlib import contextmanager
import tempfile
import shutil
import ix
from ciopath.gpath import Path


FILE_ATTR_HINTS = [
    ix.api.OfAttr.VISUAL_HINT_FILENAME_SAVE,
    ix.api.OfAttr.VISUAL_HINT_FILENAME_OPEN,
    ix.api.OfAttr.VISUAL_HINT_FOLDER,
]


class ConductorError(Exception):
    pass


@contextmanager
def waiting_cursor():
    """
    Perform some function with the wait cursor showing.
    """
    clarisse_win = ix.application.get_event_window()
    old_cursor = clarisse_win.get_mouse_cursor()
    clarisse_win.set_mouse_cursor(ix.api.Gui.MOUSE_CURSOR_WAIT)
    yield
    clarisse_win.set_mouse_cursor(old_cursor)


@contextmanager
def disabled_app():
    """
    Disble the app to perform some function.
    """
    app = ix.application
    app.disable()
    yield
    app.enable()


def is_windows():
    return os.name == "nt"


def conductor_temp_dir():
    return os.path.join(
        ix.application.get_factory().get_vars().get("CTEMP").get_string(),
        "conductor",
    )


def linuxify(filename):
    """
    Adjust reference pasths for windows.
    """
    path_regex = _get_path_line_regex()

    temp_path = tempfile.mktemp()

    shutil.copy2(filename, temp_path)
    os.remove(filename)
    with open(filename, "w+") as outfile:
        with open(temp_path, "r+") as infile:
            for line in infile:
                match = re.match(path_regex, line)
                if match:
                    try:
                        path = Path(match.group(1), no_expand=True).fslash(with_drive=False)
                        outfile.write(line.replace(match.group(1), path))
                    except ValueError:
                        outfile.write(line)
                else:
                    outfile.write(line)


def _get_path_line_regex():
    """
    Generate a regex to help identify filepath attributes.

    As we scan project files to replace windows paths, we use this regex which
    will be something like: r'\s+(?:filename|filename_sys|save_as)\s+"(.*)"\s+'
    only longer.
    """
    classes = ix.application.get_factory().get_classes()
    file_attrs = []
    for klass in classes.get_classes():
        attr_count = klass.get_attribute_count()
        for i in range(attr_count):
            attr = klass.get_attribute(i)
            hint = attr.get_visual_hint()
            if hint in FILE_ATTR_HINTS:
                file_attrs.append(attr.get_name())

    return r"\s+(?:" + "|".join(sorted(set(file_attrs))) + r')\s+"(.*)"\s+'
