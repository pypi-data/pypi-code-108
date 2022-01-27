import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jb-misc-lib",
    version="0.1.2",
    author="Jason Brown",
    author_email="jasonbrown_dev@protonmail.com",
    description="Shared code for various personal and public projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/jrbrown/jb-misc-lib",
    project_urls={
        "Bug Tracker": "https://gitlab.com/jrbrown/jb-misc-lib/-/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
        "Operating System :: POSIX"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
)

