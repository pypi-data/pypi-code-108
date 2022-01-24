from os import environ as environ, pathsep as pathsep, name as os_name
from pathlib import Path

if os_name == 'nt':
    from ctypes import cdll, windll


def _notify_environment_changed(name):
    if os_name == 'nt':
        # Put current value of environment variable into the loaded CRT library, exposing it to extensions.
        # Notes:
        #   This is a Windows-specific function, and it is assuming the extensions use the Universal CRT
        #   (Visual C++ Runtime for Visual Studio 2015 and later), not considering older CRT versions, and not
        #   doing any extra effort to make sure CRT environment used by Python itself gets the updated value.
        # Details:
        #   Modifications done via Python os.environ['name'] updates an internal Python dictionary, as well as
        #   Windows API environment. When a Python C extension library (.pyd) is imported, the dependent
        #   C Run-Time (CRT) library will be loaded with a copy of environment from Windows API. Later changes to
        #   the environment in Python and Windows API will not be reflected in the CRT copy, and therefore not seen
        #   by the extension. Since (normally) only the first extension will load the shared CRT library, with a
        #   copy of environment variables at that point in time, any additional Python extensions imported later on
        #   will also just see the same environment as the first. This function updates the environment within the
        #   currently loaded CRT library with the value currently in Python's os.environ (the value will also be
        #   written back to the Windows API, but assuming os.environ is synchronized the value should already be there).
        if windll.kernel32.GetModuleHandleW("ucrtbase.dll") != 0:
            cdll.ucrtbase._wputenv("%s=%s"%(name, environ[name]))
        if windll.kernel32.GetModuleHandleW("ucrtbased.dll") != 0:
            cdll.ucrtbased._wputenv("%s=%s"%(name, environ[name]))


def set_environment(name: str, value: str):
    environ[name] = value
    _notify_environment_changed(name)


def add_environment(name: str, value: str, skip_if_name_exists: bool = False, skip_if_value_exists: bool = True, append: bool = False, prepend: bool = False, separator: str = pathsep):
    if name not in environ:
        set_environment(name, value)
        return True
    elif not skip_if_name_exists:
        if (append or prepend) and (not skip_if_value_exists or value not in environ[name].split(separator)):
            if prepend:
                set_environment(name, value + separator + environ[name])
            else:
                set_environment(name, environ[name] + separator + value)
            return True
        elif not skip_if_value_exists or value != environ[name]:
            set_environment(name, value)
            return True
    return False


# Define path to shared runtime libraries (Boost etc)
lib_path = str((Path(__file__).parent.parent/'lib').absolute())


def add_lib_path():
    # Ensure library path is in PATH environment variable on Windows, for them to be found in runtime.
    # In developer environment this is not necessary, since these will be in path elsewhere.
    # On Linux the library path is set in the run-time search path (rpath) attribute of the libraries themselves.
    if os_name == 'nt':
        add_environment('PATH', lib_path, append=True)
