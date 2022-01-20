import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nwutils",
    version="0.3.1",
    author="Mihai Cristian Pîrvu",
    author_email="mihaicristianpirvu@gmail.com",
    description="Generic Utility functions for various projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/neuralwrappers/nwutils",
    keywords = ["utilities", "utils", "high level api"],
    packages=setuptools.find_packages(),
    install_requires=[],
    license="WTFPL",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
