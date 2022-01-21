import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aquariumlearning",  # Replace with your own username
    version="0.0.55",
    author="Quinn Johnson",
    author_email="quinn@aquarium-learn.com",
    description="Aquarium Learning Python Client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.aquariumlearning.com",
    packages=setuptools.find_packages(
        include=["aquariumlearning", "aquariumlearning.*"]
    ),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    extras_require={
        # TODO: Should these live here, or purely in CI environments?
        "typecheck": ["mypy==0.812", "pandas-stubs", "numpy==1.20.3"],
        "img": ["pillow>=8.1.0"],
    },
    install_requires=[
        "requests>=2.23.0",
        "pyarrow>=0.17.1",
        "pandas>=1.1.4",
        "numpy>=1.18.5",
        "google-resumable-media >= 1.2.0, < 2.0dev",
        "tqdm>=4.43.0",
        "termcolor>=1.1.0",
        "bs4==0.0.1",
        "importlib_metadata>=2.0.0",
        "typing-extensions>=3.7.4.3",
        "google-cloud-storage >= 1.35.1",
        "joblib==0.17.0",
        "sklearn",
        "dill",
    ],
)
