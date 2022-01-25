import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="imgz",
    version="0.0.10",

    author="cvdnn",
    author_email="cvvdnn@gmail.com",

    keywords=("pip", "license", "image", "tool"),
    description="A image util package",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/cvdnn/imgz",
    project_urls={
        "Bug Tracker": "https://github.com/cvdnn/imgz/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),

    python_requires=">=3.6",
)
