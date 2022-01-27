from setuptools import setup, find_packages
from pathlib import Path

classifiers = """
Development Status :: 1 - Planning
Intended Audience :: Science/Research
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Topic :: Utilities
Topic :: Scientific/Engineering
Topic :: Scientific/Engineering :: Artificial Intelligence
Topic :: Software Development :: Libraries :: Python Modules
License :: OSI Approved :: MIT License
"""

try:
    from Accuinsight import __about__

    about = __about__.__dict__
except ImportError:
    about = dict()
    exec(open("modeler/__about__.py").read(), about)

setup(
    name='Accuinsight',
    version=about['__version__'],
    url=about['__url__'],
    author=about['__author__'],
    description='Model life cycle and monitoring library in Accuinsight+',
    long_description=Path("README.rst").read_text(encoding="utf-8"),
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=Path("requirements.txt").read_text().splitlines(),
    setup_requires=['pytest-runner'],
    tests_require=["mock>=0.8, <3.0", "pytest==4.3.0"],
    classifiers=list(filter(None, classifiers.split("\n"))),
    zip_safe=False
)
