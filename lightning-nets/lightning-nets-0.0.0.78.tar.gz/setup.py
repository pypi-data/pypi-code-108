import os
from typing import List
import setuptools
from lightning_nets import VERSION

_PATH_ROOT = os.path.dirname(__file__)

with open("README.md", "r") as fh:
    long_description = fh.read()

def _load_requirements(path_dir: str , file_name: str = 'requirements.txt', comment_char: str = '#') -> List[str]:
    """Load requirements from a file
    >>> _load_requirements(PROJECT_ROOT)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    ['numpy...', 'torch...', ...]
    """
    with open(os.path.join(path_dir, file_name), 'r') as file:
        lines = [ln.strip() for ln in file.readlines()]
    reqs = []
    for ln in lines:
        # filer all comments
        if comment_char in ln:
            ln = ln[:ln.index(comment_char)].strip()
        # skip directly installed dependencies
        if ln.startswith('http'):
            continue
        if ln:  # if requirement is not empty
            reqs.append(ln)
    return reqs

setuptools.setup(
    name="lightning-nets",
    version=VERSION,
    author="Nick Brooks",
    author_email="nick.brooks@outlook.com",
    description="An extension to pytorch-lightning that provides trainers for generative adversarial methods",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nabrooks/lightning-nets",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    download_url='https://github.com/nabrooks/lightning-nets/tags',
    install_requires=_load_requirements(_PATH_ROOT),
)

# pip deployment is as follows:
# python setup.py sdist bdist_wheel
# twine upload dist/*