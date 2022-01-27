import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qsarmodelingpy",
    version="0.3.0",
    author="Martins, J. P. A; Reis Filho, H. M.",
    author_email="jpam@qui.ufmg.br,helitonmrf@ufmg.br",
    description="A package for building and validating QSAR models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hellmrf/QSARModelingPy",
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy>=1.20.1',
        'pandas>=1.2.2',
        'scikit-learn>=0.21.1',
        'deap>=1.3.1',
        'tqdm>=4.59.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    package_data={
        '': ['Fcritico.xlsx'],
    },
)
