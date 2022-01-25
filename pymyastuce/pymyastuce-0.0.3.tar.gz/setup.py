import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymyastuce",
    version="0.0.3",
    author="Paul Rohja LESELLIER",
    author_email="rohja@rohja.com",
    description="A small package to fetch next bus/metro/tram at a station of the MyAstuce network in Rouen, France.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Rohja/pymyastuce",
    project_urls={
        "Bug Tracker": "https://github.com/Rohja/pymyastuce/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)