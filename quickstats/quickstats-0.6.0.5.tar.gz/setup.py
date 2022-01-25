import os
import re
import setuptools
from setuptools.command.install import install

def get_macros_dir():
    """Return the installation directory, or None"""
    if '--user' in sys.argv:
        paths = (site.getusersitepackages(),)
    else:
        py_version = '%s.%s' % (sys.version_info[0], sys.version_info[1])
        paths = (s % (py_version) for s in (
            sys.prefix + '/lib/python%s/site-packages/',
            sys.prefix + '/local/lib/python%s/site-packages/',
            sys.prefix + '/lib/python%s/dist-packages/',            
            sys.prefix + '/local/lib/python%s/dist-packages/',            
            '/Library/Python/%s/site-packages/',
        ))

    for path in paths:
        if os.path.exists(path):
            return os.path.join(path, "quickstats", "macros")
    print('no installation path found', file=sys.stderr)
    return None

class CustomInstall(install):
    def run(self):
        install.run(self)
        try:
            import ROOT
            macros_dir = get_macros_dir()
            macros_path = os.path.join(macros_dir, "RooTwoSidedCBShape.cxx")
            if os.path.exists(macros_path):
                print('INFO: Found macros in "{}". Compiling...'.format(macros_path))
                ROOT.gROOT.LoadMacro('{}++'.format(macros_path))
                print('INFO: Successfully compiled ROOT macros.')
            else:
                print('WARNING: Unable to locate macro files from {}. ROOT macros will not be compiled.'.format(macros_dir))
        except:
            print('WARNING: PyROOT is not installed. ROOT macros will not be compiled.')


with open("README.md", "r") as fh:
    long_description = fh.read()
    
VERSIONFILE="quickstats/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))    

setuptools.setup(
    name="quickstats", # Replace with your own username
    version=verstr,
    author="Alkaid Cheng",
    author_email="chi.lung.cheng@cern.ch",
    description="A tool for quick statistical analysis for HEP experiments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    package_data={'quickstats':['macros/*.cxx', 'macros/*.h', 'stylesheets/*']},
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
          'numpy',
          'matplotlib',
          'click',
          'pandas',
          'uproot'
      ],
    scripts=['bin/quickstats'],
    python_requires='>=3.6',
)
