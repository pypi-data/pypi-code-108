"""
    Installation script for LHAPDF management module
"""
from setuptools import setup, find_packages

SRC_PATH = "src"

requirements = ["pyyaml", "numpy", "tqdm"]
PACKAGE = "lhapdf_management"
VERSION = "0.3"

setup(
    name=PACKAGE,
    version=VERSION,
    #version="6.4.1a",
    description="python-only lhapdf management",
    author="J.M.Cruz-Martinez",
    author_email="juacrumar@lairen.eu",
    url="https://gitlab.com/hepcedar/lhapdf/-/merge_requests/12",
    package_dir={"": SRC_PATH},
    packages=find_packages(SRC_PATH),
    entry_points={
        "console_scripts": ["lhapdf-management = lhapdf_management.scripts.lhapdf_script:main"]
    },
    zip_safe=False,
    classifiers=[
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    install_requires=requirements,
    extras_require={'fancy' : ['tqdm'], 'test': ['pytest']},
    python_requires=">=3.6",
    long_description_content_type="text/markdown",
)
