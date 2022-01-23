import os
from distutils.core import setup

README_FILE = open("README.md", "r").read()
REQUIREMENTS_FILE = f"{os.path.dirname(os.path.realpath(__file__))}/requirements.txt"

setup(
    name="argument-tasks",
    packages=["argument_tasks"],
    version="0.1",
    license="MIT",
    description="Tool to call tasks by arguments defined easily",
    long_description=README_FILE,
    long_description_content_type="text/markdown",
    author="Santiago Melo Medina",
    author_email="smelomedina05@gmail.com",
    url="https://github.com/santiagoMeloMedina/argument-tasks",
    download_url="https://github.com/santiagoMeloMedina/argument-tasks/archive/refs/tags/0.1.zip",
    keywords=[
        "Injection",
        "Singleton",
        "Simple",
    ],
    install_requires=open(REQUIREMENTS_FILE).read().splitlines(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
)
