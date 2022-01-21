#!/usr/bin/env python
from setuptools.command.build_py import build_py
from setuptools import setup
import subprocess
import os


class BuildTranslations(build_py):
    def run(self):
        translation_source_dir = os.path.join("jdAppdataEdit", "i18n")
        translation_bin_dir = os.path.join(self.build_lib, "jdAppdataEdit", "i18n")
        if not os.path.isdir(translation_bin_dir):
            os.makedirs(translation_bin_dir)
        for i in os.listdir(translation_source_dir):
            if i.endswith(".ts"):
                subprocess.run(["lrelease", os.path.join(translation_source_dir, i), "-qm", os.path.join(translation_bin_dir, i[:-3] + ".qm")])
        super().run()


with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()


setup(name="jdAppdataEdit",
    version="3.0",
    description="A graphical Program to create and edit Appdata files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="JakobDev",
    author_email="jakobdev@gmx.de",
    url="https://gitlab.com/JakobDev/jdAppdataEdit",
    download_url="https://gitlab.com/JakobDev/jdAppdataEdit/-/releases",
    python_requires=">=3.8",
    include_package_data=True,
    install_requires=[
        "PyQt6",
        "requests",
        "lxml"
    ],
    packages=["jdAppdataEdit"],
    entry_points={
        "console_scripts": ["jdappdataedit = jdAppdataEdit:main"]
    },
    cmdclass={
        "build_py": BuildTranslations,
    },
    license="GPL v3",
    keywords=["JakobDev", "PyQt6"],
    project_urls={
        "Issue tracker": "https://gitlab.com/JakobDev/jdAppdataEdit/-/issues",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Environment :: Other Environment",
        "Environment :: X11 Applications :: Qt",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Natural Language :: German",
        "Topic :: Text Editors",
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
    ],

)
