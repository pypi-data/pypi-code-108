import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fnbr",
    version="0.0.1",
    author="Chrom",
    author_email="chrom@fnbr.me",
    description="Package for video game Fortnite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://fnbr.me/tutan",
    packages=["fortnite"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
