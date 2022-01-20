from itertools import chain
from setuptools import setup, find_packages


VERSION_FILE = "dataclass2PySide6/version.py"

def get_version():
    with open(VERSION_FILE, "r") as f:
        exec(compile(f.read(), VERSION_FILE, 'exec'))
    return locals()["__version__"]


def read_readme():
    with open('README.md', encoding='utf-8') as f:
        content = f.read()
    return content


def read_requirements(path):
    with open(path, "r") as f:
        ret = f.read().splitlines()
    return ret


def get_extras_require():
    ret = {}

    ret["test"] = read_requirements("requirements/test.txt")
    ret["test-ci"] = read_requirements("requirements/test.txt") \
                     + read_requirements("requirements/test-ci.txt")
    ret['full'] = list(set(chain(*ret.values())))
    return ret


setup(
    name="dataclass2PySide6",
    version=get_version(),
    python_requires='>=3.9',
    description="Package to construct PySide6 widgets from dataclass",
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    keywords="GUI",
    classifiers=[
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    author="Jisoo Song",
    author_email="jeesoo9595@snu.ac.kr",
    maintainer="Jisoo Song",
    maintainer_email="jeesoo9595@snu.ac.kr",
    url="https://github.com/JSS95/dataclass2PySide6",
    license="LGPL",
    packages=find_packages(),
    install_requires=read_requirements("requirements/install.txt"),
    extras_require=get_extras_require(),
)