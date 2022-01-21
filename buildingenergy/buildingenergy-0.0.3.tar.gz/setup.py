import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="buildingenergy",
    version="0.0.3",
    author="Stephane Ploix",
    author_email="stephane.ploix@grenoble-inp.fr",
    description="Tools for energy management in buildings",
    long_description="buildingenergy.md",
    long_description_content_type="text/markdown",
    url="https://gricad-gitlab.univ-grenoble-alpes.fr/ploixs/h358",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)