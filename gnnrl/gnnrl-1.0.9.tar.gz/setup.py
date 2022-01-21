import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gnnrl",
    version="1.0.9",
    author="Sixing Yu",
    author_email="yusx@iastate.edu",
    description="gnnrl pipeline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yusx-swapp/GNN-RL-Model-Compression/tree/master",
    project_urls={
        "Bug Tracker": "https://github.com/anonymous429/GNN-RL-Model-Compression/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    include_package_data=True,


)