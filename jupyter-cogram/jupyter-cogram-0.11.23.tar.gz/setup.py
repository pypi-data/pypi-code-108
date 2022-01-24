import os
from pathlib import Path
from typing import Text, List, Optional

import setuptools


def get_files_in_dir(_dir: Text, prefix: Text = ".") -> List[Text]:
    return [str(Path(prefix) / o) for o in next(os.walk(_dir), (None, None, []))[2]]


data_files = [
    (
        "share/jupyter/nbextensions/jupyter-cogram",
        get_files_in_dir("jupyter_cogram", "jupyter_cogram"),
    ),
    (
        "etc/jupyter/jupyter_notebook_config.d",
        get_files_in_dir("jupyter_cogram/etc", "jupyter_cogram/etc"),
    ),
    (
        "share/jupyter/nbextensions/jupyter-cogram/jupyter_cogram_serverextension",
        get_files_in_dir(
            "jupyter_cogram/jupyter_cogram_serverextension",
            "jupyter_cogram/jupyter_cogram_serverextension",
        ),
    ),
]


def get_readme_content() -> Optional[Text]:
    # noinspection PyBroadException
    try:
        return Path("./README.md").read_text()
    except Exception:
        return None


setuptools.setup(
    name="jupyter-cogram",
    version="0.11.23",  # this is set by the CI
    url="https://cogram.com",
    author="ricwo",
    author_email="rick@cogram.com",
    description="Intuitive coding for Jupyter Notebook using natural language.",
    long_description=get_readme_content(),
    long_description_content_type="text/markdown",
    keywords=["machine learning", "NLP", "code generation", "program synthesis"],
    packages=setuptools.find_packages(),
    install_requires=[
        "notebook~=6.0",
        'importlib-metadata >= 1.0; python_version < "3.8"',
        "requests>=2.0,<3.0",
        "aiohttp~=3.7.4.post0",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Development Status :: 4 - Beta",
        "Operating System :: MacOS",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows",
        "License :: Other/Proprietary License",
    ],
    data_files=data_files,
    include_package_data=True,
    zip_safe=False,
)
