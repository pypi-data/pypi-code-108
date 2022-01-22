import os
import shutil

import setuptools

currentDir = os.getcwd()
distDir = f'{currentDir}/dist'
buildDir = f'{currentDir}/build'

if os.path.isdir(distDir):
    shutil.rmtree(distDir)

if os.path.isdir(buildDir):
    shutil.rmtree(buildDir)

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="anid",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['anid = anid.anid:anid'],
    },
    version="0.2.2",
    description="Anime Downloader",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="exebixel",
    author_email="ezequielnat7@gmail.com",
    url="https://github.com/exebixel/anid",
    install_requires=["requests", "click", "tqdm"],
    python_requires=">=3.6",
    classifiers=[
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    zip_safe=False,
)
