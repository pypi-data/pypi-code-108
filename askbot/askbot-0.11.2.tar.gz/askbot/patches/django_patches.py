"""a module for patching django"""
import imp
import hashlib
import os
import sys
import types
from django.utils.safestring import mark_safe
from django.utils.functional import lazy
from django.template import Node

try:
    from functools import WRAPPER_ASSIGNMENTS
except ImportError:
    from django.utils.functional import WRAPPER_ASSIGNMENTS

def module_has_submodule(package, module_name):
    """See if 'module' is in 'package'."""
    name = ".".join([package.__name__, module_name])
    if name in sys.modules:
        return True
    for finder in sys.meta_path:
        if finder.find_module(name):
            return True
    for entry in package.__path__:  # No __path__, then not a package.
        try:
            # Try the cached finder.
            finder = sys.path_importer_cache[entry]
            if finder is None:
                # Implicit import machinery should be used.
                try:
                    file_, _, _ = imp.find_module(module_name, [entry])
                    if file_:
                        file_.close()
                    return True
                except ImportError:
                    continue
            # Else see if the finder knows of a loader.
            elif finder.find_module(name):
                return True
            else:
                continue
        except KeyError:
            # No cached finder, so try and make one.
            for hook in sys.path_hooks:
                try:
                    finder = hook(entry)
                    # XXX Could cache in sys.path_importer_cache
                    if finder.find_module(name):
                        return True
                    else:
                        # Once a finder is found, stop the search.
                        break
                except ImportError:
                    # Continue the search for a finder.
                    continue
            else:
                # No finder found.
                # Try the implicit import machinery if searching a directory.
                if os.path.isdir(entry):
                    try:
                        file_, _, _ = imp.find_module(module_name, [entry])
                        if file_:
                            file_.close()
                        return True
                    except ImportError:
                        pass
                # XXX Could insert None or NullImporter
    else:
        # Exhausted the search, so the module cannot be found.
        return False



import itertools
import re
import random
from django.conf import settings
from django.urls import get_callable
from django.utils.safestring import mark_safe
_POST_FORM_RE = \
    re.compile(r'(<form\W[^>]*\bmethod\s*=\s*(\'|"|)POST(\'|"|)\b[^>]*>)', re.IGNORECASE)
_HTML_TYPES = ('text/html', 'application/xhtml+xml')
# Use the system (hardware-based) random number generator if it exists.
if hasattr(random, 'SystemRandom'):
    randrange = random.SystemRandom().randrange
else:
    randrange = random.randrange


from django.utils.decorators import decorator_from_middleware
from functools import wraps



def add_import_library_function():
    """TODO: Remove"""



def add_available_attrs_decorator():
    def available_attrs(fn):
        """
        Return the list of functools-wrappable attributes on a callable.
        This is required as a workaround for http://bugs.python.org/issue3445.
        """
        return tuple(a for a in WRAPPER_ASSIGNMENTS if hasattr(fn, a))
    import django.utils.decorators
    django.utils.decorators.available_attrs = available_attrs

# one may think about removing the following "patch"
# however, this use of render(_to_response) is valid in Django 1.10+

def add_render_shortcut():
    """adds `render` shortcut, introduced with django 1.3"""
    try:
        from django.shortcuts import render
    except ImportError:
        def render(request, template, data=None):
            from django.shortcuts import render_to_response
            from django.template import RequestContext
            return render_to_response(template, RequestContext(request, data))

        import django.shortcuts
        django.shortcuts.render = render


def add_hashcompat():
    """adds hashcompat module where removed
    todo: remove dependency on Coffin and then remove
    this hack"""
    import django.utils
    hashcompat = types.ModuleType('hashcompat')
    hashcompat.md5_constructor = hashlib.md5
    sys.modules['django.utils.hashcompat'] = hashcompat


from django.utils import six
from django.utils.functional import Promise
import django.utils.html

def fix_lazy_double_escape():
    """
    Wrap django.utils.html.escape to fix the double escape issue visible at
    least with field labels with localization
    """
    django.utils.html.escape = wrap_escape(django.utils.html.escape)


def wrap_escape(func):
    """
    Decorator adapted from https://github.com/django/django/pull/1007
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        for arg in list(args) + list(six.itervalues(kwargs)):
            if isinstance(arg, Promise):
                break
        else:
            return func(*args, **kwargs)
        return lazy(func, six.text_type)(*args, **kwargs)
    @wraps(wrapper)
    def wrapped(*args, **kwargs):
        return mark_safe(func(*args, **kwargs))
    return wrapped


def patch_django_template():
    import django.template
    django.template.add_to_builtins = django.template.base.add_to_builtins
    django.template.builtins = django.template.base.builtins
    django.template.get_library = django.template.base.get_library
    django.template.import_library = django.template.base.import_library
    django.template.Origin = django.template.base.Origin
    django.template.InvalidTemplateLibrary = django.template.base.InvalidTemplateLibrary

    from django.template.loaders import app_directories
    app_directories.app_template_dirs = list() #dummy value
    # from django.template.utils import get_app_template_dirs
    # later must be set to get_app_template_dirs('templates')

