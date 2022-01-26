#! /usr/bin/env python3

import os

try:
    from setuptools import find_packages, setup
except AttributeError:
    from setuptools import find_packages, setup


NAME = 'OASYS1-oasyswiser'
VERSION = '0.3.19'
ISRELEASED = True

DESCRIPTION = 'Wiser in Python'
README_FILE = os.path.join(os.path.dirname(__file__), 'README.txt')
LONG_DESCRIPTION = open(README_FILE).read()
AUTHOR = 'Michele Manfredda, Lorenzo Raimondi, Luca Rebuffi, Aljosa Hafner'
AUTHOR_EMAIL = 'michele.manfredda@elettra.eu'
URL = 'https://github.com/oasys-elettra-kit/OasysWiser'
DOWNLOAD_URL = 'https://github.com/oasys-elettra-kit/OasysWiser'
MAINTAINER = 'Aljosa Hafner'
MAINTAINER_EMAIL = 'aljosa.hafner@ceric-eric.eu'
LICENSE = 'GPLv3'

KEYWORDS = [
    'waveoptics',
    'simulator',
    'oasys1'
]

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: X11 Applications :: Qt',
    'Environment :: Console',
    'Environment :: Plugins',
    'Programming Language :: Python :: 3',
    'Intended Audience :: Science/Research'
]

SETUP_REQUIRES = (
    'setuptools'
)

INSTALL_REQUIRES = (
    'LibWiser>=0.12.13',
    'oasys1>=1.1.19',
    'wofrywiser>=0.1.4'
)

PACKAGES = find_packages(exclude=('*.tests', '*.tests.*', 'tests.*', 'tests'))

PACKAGE_DATA = {
    "orangecontrib.wiser.widgets.light_sources":["icons/*.png", "icons/*.jpg"],
    "orangecontrib.wiser.widgets.optical_elements":["icons/*.png", "icons/*.jpg"],
    "orangecontrib.wiser.widgets.tools":["icons/*.png", "icons/*.jpg"]
}

NAMESPACE_PACAKGES = ["orangecontrib",
                      "orangecontrib.wiser",
                      "orangecontrib.wiser.widgets"]

ENTRY_POINTS = {
    'oasys.addons' : ("wise = orangecontrib.wiser" ),
    'oasys.widgets' : (
        "Wiser Light Sources = orangecontrib.wiser.widgets.light_sources",
        "Wiser Optical Elements = orangecontrib.wiser.widgets.optical_elements",
        "Wiser Tools = orangecontrib.wiser.widgets.tools"
    ),
    'oasys.menus' : ("wisemenu = orangecontrib.wiser.menu")
}

if __name__ == '__main__':
    is_beta = False

    try:
        import PyMca5, PyQt4

        is_beta = False
    except:
        setup(
              name = NAME,
              version = VERSION,
              description = DESCRIPTION,
              long_description_content_type = 'text/markdown',
              long_description = LONG_DESCRIPTION,
              author = AUTHOR,
              author_email = AUTHOR_EMAIL,
              url = URL,
              download_url = DOWNLOAD_URL,
              license = LICENSE,
              keywords = KEYWORDS,
              classifiers = CLASSIFIERS,
              packages = PACKAGES,
              package_data = PACKAGE_DATA,
              #          py_modules = PY_MODULES,
              setup_requires = SETUP_REQUIRES,
              install_requires = INSTALL_REQUIRES,
              #extras_require = EXTRAS_REQUIRE,
              #dependency_links = DEPENDENCY_LINKS,
              entry_points = ENTRY_POINTS,
              namespace_packages=NAMESPACE_PACAKGES,
              include_package_data = True,
              zip_safe = False,
              )

    if is_beta: raise NotImplementedError("This version of WISE 2 doesn't work with Oasys1 beta.\nPlease install OASYS1 final release: http://www.elettra.eu/oasys.html")
