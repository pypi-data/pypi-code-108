import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="GReNaDIne",
    version="0.0.19",
    author="Sergio Peignier, Pauline Schmitt",
    author_email="sergio.peignier@insa-lyon.fr",
    description="Data-Driven Gene Regulatory Network Inference",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'scikit-learn',
        'tqdm',
        'scipy',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
)

print(setuptools.find_packages())
