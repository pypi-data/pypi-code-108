from setuptools import find_packages, setup

with open("albion_similog/__init__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.strip().split("=")[1].strip(" '\"")
            break
    else:
        __version__ = "0.3.5"

with open("README.md", "rb") as f:
    readme = f.read().decode("utf-8")

install_requires = [
    "cython==0.29.21",
    "numpy~=1.19",
    "pandas~=1.3",
    "scikit-learn~=1.0",
    "scikit-bio==0.5.6",
    "biopython==1.78",
    "changepoint-cython==0.1.3",  # numpy and cython must be installed to build
]

extra_requirements = {
    "dev": [
        "pytest==6.1.1",
        "black~=21.12b0",
        "flake8==3.8.4",
        "pylint==2.6.0",
        "pre-commit==2.7.1",
    ]
}

setup(
    name="albion_similog",
    version=version,
    description="Compute a consensus dataseries with FAMSA algorithm.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Oslandia",
    author_email="infos@oslandia.com",
    maintainer="Oslandia",
    maintainer_email="infos@oslandia.com",
    url="",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    install_requires=install_requires,
    extras_require=extra_requirements,
    packages=find_packages(),
)
