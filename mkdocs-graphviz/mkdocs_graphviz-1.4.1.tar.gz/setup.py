import os
import sys
from setuptools import setup

VERSION = '1.4.1'

if sys.argv[-1] == 'publish':
    if os.system("pip freeze | grep wheel"):
        print("wheel not installed.\nUse `pip install wheel`.\nExiting.")
        sys.exit()
    if os.system("pip freeze | grep twine"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    print("You probably want to also tag the version now:")
    print("  git tag -a {0} -m 'version {0}'".format(VERSION))
    print("  git push --tags")
    sys.exit()

setup(
    name="mkdocs_graphviz",
    version=VERSION,
    py_modules=["mkdocs_graphviz"],
    install_requires=['Markdown>=2.3.1'],
    author="Rodrigo Schwencke",
    author_email="dev.hopper@lyceeperier.fr",
    description="Render Graphviz graphs in Mkdocs, as inline SVGs and PNGs, directly from your Markdown (python3 version)",
    long_description_content_type="text/markdown",
    long_description="""Project Page : [rodrigo.schwencke/mkdocs-graphviz](https://gitlab.com/rodrigo.schwencke/mkdocs-graphviz)

Some examples in these pages:

* Trees : https://eskool.gitlab.io/tnsi/donnees/arbres/quelconques/
* Graphs : https://eskool.gitlab.io/tnsi/donnees/graphes/definitions/

This is a continuation of the great initial job of :

* All newer Credits: [rodrigo.schwencke/mkdocs-graphviz](https://gitlab.com/rodrigo.schwencke/mkdocs-graphviz)
* Cesare Morel [cesaremorel/markdown-inline-graphviz](https://github.com/cesaremorel/markdown-inline-graphviz), and before him,
* Steffen Prince in [sprin/markdown-inline-graphviz](https://github.com/sprin/markdown-inline-graphviz), 
* Initially inspired by Jawher Moussa [jawher/markdown-dot](https://github.com/jawher/markdown-dot)
    
In order to get it work with pip (python3) and mkdocs.

If you use python 2, please use the original extension instead.""",
    license="MIT",
    url="https://gitlab.com/rodrigo.schwencke/mkdocs-graphviz.git",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Documentation',
        'Topic :: Text Processing',
        'License :: OSI Approved :: MIT License',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows 10',
    ],
)
