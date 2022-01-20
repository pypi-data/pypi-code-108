import re
import setuptools
import masterful.version as version
from pkg_resources import get_distribution, DistributionNotFound

with open("README", "r") as fh:
  long_description = fh.read()

INSTALL_REQUIRES = [
    'protobuf',
    'pandas',
    'plotly',
    'inject',
    'tensorflow_addons',
    'psutil',
    'packaging',
    'typing_extensions',
    'tqdm',
    'memory_tempfile',
    'requests',
    'dataclasses',
    'albumentations',
    'masterful-gui==0.3.6',
]

ALT_INSTALL_REQUIRES = {}


def check_alternative_installation(install_require,
                                   alternative_install_requires):
  """If some version version of alternative requirement installed, return alternative,
    else return main.
    """
  for alternative_install_require in alternative_install_requires:
    try:
      alternative_pkg_name = re.split(r"[!<>=]", alternative_install_require)[0]
      get_distribution(alternative_pkg_name)
      return str(alternative_install_require)
    except DistributionNotFound:
      continue

  return str(install_require)


def get_install_requirements(main_requires, alternative_requires):
  """Iterates over all install requires
    If an install require has an alternative option, check if this option is installed
    If that is the case, replace the install require by the alternative to not install dual package"""
  install_requires = []
  for main_require in main_requires:
    if main_require in alternative_requires:
      main_require = check_alternative_installation(
          main_require, alternative_requires.get(main_require))
    install_requires.append(main_require)

  return install_requires


INSTALL_REQUIRES = get_install_requirements(INSTALL_REQUIRES,
                                            ALT_INSTALL_REQUIRES)

setuptools.setup(
    name="masterful",
    version=version.__version__,
    author="Masterful AI",
    author_email="learn@masterfulai.com",
    description="Masterful AutoML Platform.",
    long_description_content_type="text/markdown",
    long_description=long_description,
    license_files=('LICENSE',),
    license='Copyright 2022, Masterful AI, Inc.',
    url="http://masterfulai.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=INSTALL_REQUIRES,
    python_requires=">=3.6",
)