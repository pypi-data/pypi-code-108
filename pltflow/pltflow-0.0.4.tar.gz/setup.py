from setuptools import find_packages, setup

base_dependencies = [
    "pandas>=1.0.0",
    "python-dateutil>=2",
    "seaborn>0.9.0",
    "rutil>=0.0.1",
    "matplotlib>=2.2",
]


additional_dependencies = {
    "dev": ["black>=21.9b0", "pre-commit>=2.15.0", "pytest>=6.2.1", "pylint>=2.7.4", "jupyterlab", "twine"],
}

VERSION = "0.0.4"
DESCRIPTION = "A matplotlib/seaborn wrapper to create beautiful plots with predefined styles using pipelines"

with open("README.md", "r", encoding="utf8") as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name="pltflow",
    packages=find_packages(),
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Ismael Cabral",
    version=VERSION,
    keywords=["matplotlib", "seaborn", "plt", "plot", "graphs", "data", "visualization", "pandas"],
    install_requires=base_dependencies,
    extras_require=additional_dependencies,
    python_requires=">=3.6",
)
