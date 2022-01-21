from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='fichub-cli-metadata',
    author='Arbaaz Laskar',
    author_email="arzkar.dev@gmail.com",
    description="A metadata plugin for fetching Metadata from the Fichub API for the fichub-cli",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version='0.1.2',
    license='MIT',
    url="https://github.com/fichub-cli-contrib/fichub-cli-metadata",
    packages=find_packages(
        include=['fichub_cli_metadata', 'fichub_cli_metadata.*']),
    include_package_data=True,
    install_requires=[
        'fichub-cli>=0.5'
    ],
    entry_points='''
        [console_scripts]
        fichub_cli_metadata=fichub_cli_metadata.cli:app
    ''',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
