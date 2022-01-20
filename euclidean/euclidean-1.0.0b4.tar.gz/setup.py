from setuptools import setup, find_packages


def readme():
    with open("README.rst", "r") as f:
        return f.read()


CLASSIFIERS = []
KEYWORDS = ["euclidean", "geometry", "vector", "point", "polygon"]
PROJECT_URLS = {}


INSTALL_REQUIRES = ["sortedcontainers>=2", "multipledispatch>=0.6"]
TESTS_REQUIRE = ["pytest", "coverage"]
EXTRAS_REQUIRE = {
    "docs": [],
    "tests": TESTS_REQUIRE,
    "siquant": ["siquant==4.0.0b6"],
    "dev": TESTS_REQUIRE + ["pre-commit"],
}

setup(
    name="euclidean",
    version="1.0.0b4",
    description="Euclidean Geometry Library",
    long_description=readme(),
    url="https://github.com/keystonetowersystems/euclidean",
    project_urls=PROJECT_URLS,
    author="Greg Echelberger",
    author_email="greg@keystonetowersystems.com",
    packages=find_packages(exclude=("tests",)),
    setup_requires=[],
    extras_require=EXTRAS_REQUIRE,
    install_requires=INSTALL_REQUIRES,
    zip_safe=True,
)
