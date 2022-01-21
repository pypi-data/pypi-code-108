import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent.parent

VERSION = "0.0.5"
DESCRIPTION = "logging_fastapi"
# The text of the README file
README = (HERE / "README.md").read_text()
# Setting up
setup(
    name="logging_fastapi",
    version=VERSION,
    author="Horváth Dániel",
    author_email="nitedani@gmail.com",
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "cuid",
        "loguru",
        "psutil",
        "pydash",
        "schedule",
        "httpx",
    ],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'
    keywords=["logger", "fastapi", "loki"],
    classifiers=[
        "Development Status :: 3 - Alpha",
    ],
)
