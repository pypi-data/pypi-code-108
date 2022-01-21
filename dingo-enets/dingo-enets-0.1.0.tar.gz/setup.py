from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()
VERSION = "0.1.0"

setup(
    name="dingo-enets",
    description="Neural networks for feature extraction for gravitational waves.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/max-dax/dingo-enets/",
    license="MIT",
    author="Maximilian Dax",
    version=VERSION,
    packages=["dingo_enets"],
    python_requires=">=3.6",
    install_requires=["numpy", "torch", "nflows", "pyyaml", "gdown", "textwrap3"],
    extras_require={
        "dev": [
            "pytest",
            "black",
        ],
    },
)
