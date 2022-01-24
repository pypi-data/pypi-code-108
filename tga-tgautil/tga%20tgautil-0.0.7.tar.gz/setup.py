import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tga tgautil",
    version="0.0.7",
    author="DSC Developer",
    author_email="1106896377@qq.com",
    description="Some useful util tools for tga",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jewdore/tga-utils.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)