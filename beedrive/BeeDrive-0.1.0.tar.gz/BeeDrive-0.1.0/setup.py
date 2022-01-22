import sys

import setuptools

sys.path.append("../../")

import beedrive


setuptools.setup(
    name=beedrive.__name__,
    version=beedrive.__version__,
    description="BeeDrive: Open Source Privacy File Transfering System for Teams and Individual Developers",
    long_description=open("../../README.md", encoding="utf8").read(),
    long_description_content_type='text/markdown',
    url="https://github.com/JacksonWuxs/BeeDrive",
    author="Xuansheng Wu",
    maintainer="Xuansheng Wu",
    platforms=["all"],
    packages=setuptools.find_packages(where="beedrive",
                                      exclude=("distribute_exe",
                                               "distribute_pip",)),
    license="GPL v3",
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        "Programming Language :: Python :: 3",
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        ],
    entry_points={"console_scripts": "beedrive=beedrive.__main__:main",
                  "gui_scripts": "beedrive-gpu=beedrive.app:main"}
    )
    
        

