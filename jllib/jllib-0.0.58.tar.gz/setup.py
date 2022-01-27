import setuptools


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jllib",
    version="0.0.58",
    author="Jonathan Liebers",
    author_email="git@jo2k.de",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://example.org",
    packages=[
        'jllib',
        'jllib.models',
        'jllib.utils'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=parse_requirements('requirements.txt')
)

# TODO twine not needed as requirement for user