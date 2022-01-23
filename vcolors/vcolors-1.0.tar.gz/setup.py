from setuptools import setup, find_packages

VERSION = '1.0'
DESCRIPTION = 'Your terminal colored and pretty printed'
LONG_DESCRIPTION = 'A package that allows you to print colored text to the terminal, extends pprint and colored'

# Setting up
setup(
    name="vcolors",
    version=VERSION,
    author="Victor Valar",
    author_email="<victoribeirodosantos@hotmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['colored'],
    keywords=['python','colored', 'pprint','print','terminal'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)