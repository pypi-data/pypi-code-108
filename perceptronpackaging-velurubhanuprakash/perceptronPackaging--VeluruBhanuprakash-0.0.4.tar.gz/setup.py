import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

PKG_NAME = "perceptronPackaging"
USER_Name = "VeluruBhanuprakash"
PROJECT_NAME = "perceptronPackaging"
setuptools.setup(
    name=f"{PKG_NAME}--{USER_Name}",
    version="0.0.4",
    author=USER_Name,
    author_email="bhanuprakash@gmail.com",
    description="A small package of perceptron",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/{USER_Name}/{PROJECT_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{USER_Name}/{PROJECT_NAME}/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "numpy",
        "joblib",
        "pandas",

    ]
)