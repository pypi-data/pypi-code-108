from setuptools import find_packages, setup
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="harrix-pylib",
    version="0.9",
    description="Different functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Harrix/harrix-pylib",
    author="Anton Sergienko",
    author_email="anton.b.sergienko@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    zip_safe=False
)
