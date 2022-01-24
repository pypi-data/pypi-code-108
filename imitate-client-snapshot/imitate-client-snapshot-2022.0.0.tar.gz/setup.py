from setuptools import setup, find_packages  # noqa: H301

NAME = "imitate-client-snapshot"
VERSION = "2022.0.0"

DESC = "imitate-client for python."

f = open("requirements.txt", "r")

REQUIRES = f.readlines()
AUTHOR = "joecqupt"
AUTHOR_EMAIL = "joe469391363@gmail.com"

setup(
    name=NAME,
    version=VERSION,
    description=DESC,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url="",
    keywords=["mq", "client"],
    python_requires=">=3.6",
    install_requires=REQUIRES,
    packages=find_packages(exclude=["test", "tests"]),
    include_package_data=True,
    long_description=DESC
)
