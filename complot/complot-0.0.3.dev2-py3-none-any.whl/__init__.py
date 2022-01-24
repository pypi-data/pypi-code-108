import os
import pkgutil
import importlib
import inspect

PACKAGE_PATH = os.path.dirname(os.path.abspath(__file__))


def get_exposed_package_objects(path:str) -> dict:
  r'''
  Process a given path, taking all the exposed objects in it and returning
  a dictionary with their names and respective pointers.

  Parameters
  ----------
  path: str
  Path

  Returns
  -------
  dict(str, object)
  Names and objects to be exposed
  '''
  pkg = os.path.normpath(path[path.rfind('complot'):]).replace(os.sep, '.')
  ans = {}

  all_modules = []
  for _, module_name, _ in pkgutil.walk_packages([path]):
    all_modules.append(module_name)
  all_modules.sort()

  for module_name in all_modules:
    if module_name.endswith('setup') or module_name.endswith('__'): continue
    # Import all classes and functions
    if module_name not in ['core.device', 'core.multi_par', 'core.types']:
      mod = importlib.import_module('.' + module_name, package=pkg)

      for n, c in inspect.getmembers(mod):
        if n in mod.__all__:
          ans[n] = c

  return ans


objs = get_exposed_package_objects(PACKAGE_PATH)
globals().update(objs)


__all__ = ['PACKAGE_PATH']
__all__ += list(objs.keys())
__all__.sort()
