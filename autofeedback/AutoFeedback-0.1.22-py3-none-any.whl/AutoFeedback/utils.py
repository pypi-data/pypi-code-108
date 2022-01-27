def check_module(modname):
    from importlib.util import find_spec
    installed = find_spec(modname) is not None
    if not installed:
        import subprocess
        import sys
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", modname])
    return
