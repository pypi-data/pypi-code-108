import setuptools
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "src/absfuyu", "version.py")) as fp:
    exec(fp.read())


setuptools.setup(
    name="absfuyu",
    version=__version__,
    author="somewhatcold (AbsoluteWinter)",
    author_email="",
    description="A small collection of code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AbsoluteWinter/absfuyu",
    project_urls={
        "Bug Tracker": "https://github.com/AbsoluteWinter/absfuyu/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Natural Language :: English",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6, <4",
    install_requires=["absfuyu"],
)

# python -m build
# python setup.py sdist bdist_wheel
# twine upload dist/*