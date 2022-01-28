import setuptools

with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()

setuptools.setup(
    name="iso-dl",
    version="0.1",
    author="txhx38",
    author_email="txhx38@gmail.com",
    description="Download Linux ISOs quickly from the command line.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/txhx38/iso-dl",
    project_urls={
        "Bug Tracker": "https://github.com/txhx38/iso-dl/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    scripts=["bin/iso-dl"],
)
