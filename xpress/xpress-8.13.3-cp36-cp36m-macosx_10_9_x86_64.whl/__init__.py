import os
import os.path
import sys
import platform
import re
from . import __version_file__

oldcwd = os.getcwd()
base_path = os.path.dirname(os.path.realpath(__file__))

if platform.system() == 'Windows':

    added_dll = None

    if 'PATH' in os.environ:
        curpath = os.environ['PATH']
    else:
        curpath = ''

    # Check if safe dll addition is provided (None is to avoid
    # throwing an exception in case attribute is not there).
    if getattr(os, 'add_dll_directory', None):
        added_dll = os.add_dll_directory(base_path + '\\lib')
        os.environ['PATH'] = base_path + '\\lib' + ';' + curpath
    else:
        os.environ['PATH'] = base_path + '\\lib' + ';' + base_path + \
            '\\..\\..;' + curpath

    del curpath


if platform.system() == 'Windows':
    default_xpressmp = 'c:\\xpressmp'
elif platform.system() == 'Darwin':
    default_xpressmp = '/Applications/FICO Xpress/xpressmp'
else:
    default_xpressmp = '/opt/xpressmp'


def manual():
    """Returns the full path to the PDF reference manual of the Python
    interface.

    Syntax: xpress.manual()

    Note that only the manual of the Python interface (in PDF format)
    is included in the PyPI and conda package downloaded from these
    repositories; the PDF version of all other Xpress-related
    documentation is contained in the Xpress distribution, and on the
    on-line, HTML format documentation is available on the FICO web
    pages.

    The online documentation includes that for the Xpress Optimizer
    and the Nonlinear solvers and can be found at
    https://www.fico.com/fico-xpress-optimization/docs/latest/overview.html
    """

    import os.path

    return os.path.join(base_path, "doc", "python-interface.pdf")


def examples():
    """
    Returns the full path to the directory containint the examples
    that come with the Python interface.

    Syntax: xpress.examples()

    In the modeling_examples/ subdirectory you will find some of the Mosel
    examples translated into their Python counterpart.

    The online documentation includes that for the Xpress Optimizer and
    the Nonlinear solvers and can be found at
    https://www.fico.com/fico-xpress-optimization/docs/latest/overview.html
    """

    import os
    import os.path

    return os.path.join(base_path, "examples") + os.sep


def check_lic_version(path):
    """Check license file version against the Xpress library version. If
    the license is more recent, all should be good, otherwise throw up a
    warning (no need to block as the "import xpresslib" will fail).
    """

    global __version__

    found_lic = False
    if os.path.isdir(path):
      for ext in ['xpr', 'ini', 'lic', 'txt']:
        lic_file = os.path.join(path, 'xpauth.' + ext)
        if os.path.isfile(lic_file):
          found_lic = True
          break
    elif os.path.isfile(path):
      lic_file = path
      found_lic = True

    if not found_lic:
      print('Warning: License file was not found at "' + path + '". ' +
            'Importing xpress may fail.')
      return None, None

    try:
        license = open(lic_file)
    except:
        if filename is None:
            print('Warning: Could not open license file "' + lic_file + '". ' +
                  'Importing xpress may fail.')
        return None, None

    licmajor, licminor = None, None

    for line in license.readlines():

        s = re.match('.*fico_xpress_release=\"([0-9]*)\\.([0-9]*)\".*', line)

        if s:
            licmajor = int(s.group(1))
            licminor = int(s.group(2))
            break
        elif re.match('EOF.*', line):
            break

    license.close()

    if licmajor is not None and \
       licminor is not None:

        split_ver = __version__.split('.')
        vermajor = int(split_ver[0])
        verminor = int(split_ver[1])

        if vermajor > licmajor or \
           ((vermajor == licmajor) and
            (verminor > licminor)):
            print('Warning: Your license version ' +
                  str(licmajor) + '.' + str(licminor) +
                  ' appears to be less recent than the version ' +
                  str(__version__) +
                  ' of the installed module. This might be cause for a failed ' +
                  'import. Please upgrade your license or install an older ' +
                  'version of the Xpress module; you can do the latter with\n\n' +
                  'pip uninstall xpress\n' +
                  'pip install xpress==x.y.z\n\n' +
                  '(please check the release history at ' +
                  'https://pypi.org/project/xpress/#history) or with conda:\n\n' +
                  'conda install xpress=x.y.z\n')

    return licmajor, licminor


__version__ = __version_file__.__version__
__version_library__ = __version_file__.__version_library__


# If the XPAUTH_PATH environment variable is not set, set it ourselves.
# Then check license number against that of __version__ and give a
# warning if they differ (i.e. if version is more recent than license
# file

def _init_license():
    lic_env_var = None
    if os.environ.get('XPRESS', ''):
        if os.environ.get('XPAUTH_PATH', ''):
            licpath = os.environ['XPAUTH_PATH']
            lic_env_var = 'XPAUTH_PATH'
            if os.environ['XPRESS'] != os.environ['XPAUTH_PATH']:
                print('The XPRESS and XPAUTH_PATH environment variables are set to ' +
                      'different paths. The license from XPAUTH_PATH will be used: ' +
                      licpath)
        else:
            licpath = os.environ['XPRESS']
            lic_env_var = 'XPRESS'
    elif os.environ.get('XPAUTH_PATH', ''):
        licpath = os.environ['XPAUTH_PATH']
        lic_env_var = 'XPAUTH_PATH'
    else:
        # Neither variable is set - look for an Xpress installation
        xpressmp = os.environ.get('XPRESSDIR', default_xpressmp) or default_xpressmp
        xpressmp_lic = os.path.join(xpressmp, 'bin', 'xpauth.xpr')
        if os.path.isfile(xpressmp_lic):
            licpath = xpressmp_lic
            if os.environ.get('XPRESSDIR', ''):
                lic_env_var = 'XPRESSDIR'
            else:
                lic_env_var = 'default_xpressmp'  # Special value, not an environment variable
        else:
            # Use the license included with the Python module
            licpath = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                'license',
                'community-xpauth.xpr')
            print("Using the Community license in this session. If you have a full " +
                  "Xpress license, first set the XPAUTH_PATH environment variable to the " +
                  "full path to your license file, xpauth.xpr, and then restart " +
                  "Python. If you want to use the FICO Community license and no longer " +
                  "want to see this message, set the XPAUTH_PATH environment variable to: " +
                  licpath + '\n' + "NB: setting XPAUTH_PATH will also affect any " +
                  "other Xpress products installed on your system.")

    if not os.path.isabs(licpath):
        licpath = os.path.join(oldcwd, licpath)

    # Set XPAUTH_PATH so that Xpress uses the correct license - this works on both Windows and Unix
    os.environ['XPAUTH_PATH'] = licpath
    return licpath, lic_env_var


licpath, lic_env_var = _init_license()

# Check license version against library version
licmaj, licmin = check_lic_version(licpath)


# Try to import the actual library. Once its members/methods are
# imported with "from ... import *" all symbols become those of the
# xpress module.

try:
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    from xpresslib import *

except:
    print('Could not import xpress module. ' +
          'We detected that the Xpress Python interface is version ' +
          __version__ + ' and the license file is for version ' +
          str(licmaj) + '.' + str(licmin) + '. Please check that the ' +
          'versions match any installation of the FICO Xpress Optimization ' +
          'suite you may have.\n\n' +
          'If you have a full installation of the FICO Xpress Optimization suite ' +
          'version 8.5.2 or earlier, you should delete all files named ' +
          'xpress*.pyd in the c:\\xpressmp\\bin directory and ' +
          'subdirectories (this may vary depending on where the ' +
          'FICO Xpress installation is located). On Linux or MacOS ' +
          'systems, delete all files named xpress*.so in ' +
          '/opt/xpressmp/lib.')

    raise

else:

    # Check that version in xprs.lib is the same as the one saved in
    # __version__.py

    try:

        libver = getversion()

        split_libver = libver.split('.')
        split_intver = __version_library__.split('.')

        if split_libver[0] != split_intver[0]:
            print('The Xpress Python API version ' + __version_library__ +
                  ' found the Xpress libraries version ' + libver +
                  '. Those versions are incompatible. If you have a local ' +
                  'Xpress installation in addition to the Xpress package in ' +
                  'Python, then please make sure that both Xpress ' +
                  'installations have the same version number.')
        elif __version_library__ != libver:
            print('Warning: The Xpress Python interface\'s version does not ' +
                  'match that of the Xpress Optimizer library:\n\n' +
                  __version_library__ + '!=' + libver +
                  '\n\nWhile the two versions are compatible, you may want '
                  'to check your installation')

        del split_libver
        del split_intver

    except InterfaceError as e:

        # Only raise the exception on non-OEM licenses
        if "OEM" not in e.args[0].split(' '):
            if lic_env_var:
                if lic_env_var == 'default_xpressmp':
                    lic_location_msg = 'in the default Xpress installation directory'
                else:
                    lic_location_msg = 'using the ' + lic_env_var + ' environment variable'
                print('The license file was located ' + lic_location_msg + ': ' + licpath + '. ' +
                      'To use an alternative license file, set the XPAUTH_PATH environment variable ' +
                      'to the full path to your license file, xpauth.xpr. NB: setting XPAUTH_PATH ' +
                      'will also affect any other Xpress products installed on your system.\n')
                del lic_location_msg

            raise

    except:

        print('Unable to obtain the Xpress Optimizer library version. ' +
              'Please check your installation and/or the license file.')

        raise
finally:
    os.chdir(oldcwd)


# Close import; delete all temporary variables and modules

if platform.system() == 'Windows':
    if added_dll is not None:
        added_dll.close()
    del added_dll

# Local variables
del oldcwd, default_xpressmp
del __version_file__
del licpath, lic_env_var
del licmaj, licmin

# Local methods
del check_lic_version
del _init_license

# External modules
del os
del sys
del platform
del re
