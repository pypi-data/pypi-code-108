import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
Project_NAME="mypackage"
USER_NAME="divyamtalreja"

setuptools.setup(
    name=f"{Project_NAME}-{USER_NAME}",
    version="0.0.1",
    author=USER_NAME,
    author_email="divyamtalreja16@gmail.com",
    description="implementation of  perceptron",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/{USER_NAME}/{Project_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{USER_NAME}/{Project_NAME}/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=[
        "numpy",
        "pandas"
    ]
)