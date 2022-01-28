from setuptools import find_packages, setup

base_dependencies = [
    "pandas>=1.0.0",
    "python-dateutil>=2",
]


additional_dependencies = {
    "dev": [
        "black>=21.9b0",
        "pre-commit>=2.15.0",
        "pytest>=6.2.1",
        "pylint>=2.7.4",
        "jupyterlab",
        "twine",
        "seaborn",
    ],
}

VERSION = "0.0.1"
DESCRIPTION = "R original utilities now in python"

with open("README.md", "r", encoding="utf8") as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name="rutil",
    packages=find_packages(where="rutil"),
    package_dir={"": "rutil"},
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Ismael Cabral",
    version="0.0.2",
    py_modules=["rutil"],
    keywords=["R language", "R", "str()", "pandas", "struture"],
    install_requires=base_dependencies,
    extras_require=additional_dependencies,
    python_requires=">=3.6",
)
