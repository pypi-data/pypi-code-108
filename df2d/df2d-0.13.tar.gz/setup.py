from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="df2d",
    version="0.13",
    packages=["df2d"],
    author="Semih Gunel",
    author_email="gunelsemih@gmail.com",
    description="2D pose estimation pipeline for tethered Drosophila.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/semihgunel/Drosophila2DPose",
)
