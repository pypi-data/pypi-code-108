import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rivals-top8-results",
    version="1.0.1",
    author="Impasse52",
    author_email="giuseppe.termerissa@gmail.com",
    description="Small Pillow library useful in creating automatic Rivals of Aether Top 8 Results screens ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Impasse52/rivals-top8-results",
    project_urls={
        "Bug Tracker": "https://github.com/Impasse52/rivals-top8-results/issues",
    },
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)