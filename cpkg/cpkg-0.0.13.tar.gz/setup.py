import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cpkg",
    version="0.0.13",
    author="xiongtianshuo",
    author_email="Mr_Xiongts@163.com",
    description="A package that creates a package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seoul2k/cPkg",
    project_urls={
        "Bug Tracker": "https://github.com/seoul2k/cPkg/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=['cpkg/'],
    python_requires=">=3.6",
    install_requires=['cpkgtab==0.0.3'],
)
