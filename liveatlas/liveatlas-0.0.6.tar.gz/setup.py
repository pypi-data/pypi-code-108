from setuptools import setup, find_packages

VERSION = '0.0.6'
DESCRIPTION = 'liveatlas-API'
LONG_DESCRIPTION = 'A package providing methods for interacting with a liveatlas dynamic map'

# Setting up
setup(

    name="liveatlas",
    version=VERSION,
    author="Sam",
    author_email="",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['datetime', 'requests', 're'],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'

    keywords=['python', 'first package'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)