import setuptools
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

thelibFolder = os.path.dirname(os.path.realpath(__file__))
requirementPath = thelibFolder + '/requirements.txt'
install_requires = [] 
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

setuptools.setup(
    name="acat", 
    version="1.2.9",
    author="Shuang Han",
    author_email="hanshuangshiren@gmail.com",
    description="Alloy Catalysis Automated Toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/asm-dtu/acat",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: POSIX",
    ],
    install_requires=install_requires,
    python_requires='>=3.6',
)
