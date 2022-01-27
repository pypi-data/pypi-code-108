import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="d20-orm",
    version="1.0.0alpha5",
    author="Alex Sánchez Vega",
    author_email="alex@d20.services",
    description="A small ORM for multimodel DBs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/d20services/arangodb_python_orm",
    project_urls={
        "Bug Tracker": "https://github.com/d20services/arangodb_python_orm/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=['pyArango', 'datetime'],
)