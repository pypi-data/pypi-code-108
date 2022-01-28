import setuptools

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="net-switch-tools",
    version="0.0.3",
    author="Justin Turney",
    author_email="info@justinturney.com",
    description="A package for managing network switches",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/greenfructose/net-switch-tools",
    project_urls={
        "Bug Tracker": "https://github.com/greenfructose/net-switch-tools/issues",
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
