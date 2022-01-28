import setuptools

from phases import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="phases",
    version=__version__,
    author="Franz Ehrlich",
    author_email="fehrlichd@gmail.com",
    description="An Execution Framework for pyPhase projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/tud.ibmt/phases",
    packages=setuptools.find_packages(exclude=["tests", "example"]),
    test_suite="tests",
    install_requires=["docopt", "pyPhases", "PyYAML", "pystache"],
    include_package_data=True,
    package_data={"phases": ["generate-template/*", "generate-template/**/*", "static-template/*", "static-template/**/*"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "phases=phases.cli:main",
        ],
    },
)
