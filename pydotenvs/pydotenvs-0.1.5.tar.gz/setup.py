import setuptools
from pydotenvs import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pydotenvs",
    version=__version__,
    author="AbleInc - Jaylen Douglas",
    author_email="douglas.jaylen@gmail.com",
    description="Import environment variables from your .env file or run as command line tool; PyDotEnv Cli.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ableinc/pyenv",
    keywords=['environment variables', 'deployments', 'settings', 'env', 'pydotenvs',
              'configurations', 'python', 'pydotenvs', 'python3', 'dependencies'],
    packages=['pydotenvs'],
    entry_points='''
        [console_scripts]
        pyenv=pydotenvs.cli:pyenv
    ''',
    install_requires=[
          'click>=7.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
