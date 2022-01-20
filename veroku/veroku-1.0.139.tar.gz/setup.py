import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]

setuptools.setup(
    name="veroku",
    author="EJ Louw",
    author_email="ejlouw00@gmail.com",
    description="An open source library for building and performing inference with probabilistic graphical models.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="BSD 3-Clause License",
    url="https://github.com/ejlouw/veroku",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIREMENTS,
    python_requires='>=3.6')
