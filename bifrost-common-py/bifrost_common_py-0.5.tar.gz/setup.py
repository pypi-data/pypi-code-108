import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = 'bifrost_common_py',
    packages = ['bifrost_common_py'],
    version = '0.5',  # Ideally should be same as your GitHub release tag varsion
    description = 'Common python library functions for interacting with BIFROST.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author = 'Manuel Matzinger',
    author_email = 'bifrost.at@siemens.com',
    url = 'https://bifrost.siemens.com/en',
    download_url = '',
    keywords = ['bifrost', 'bifrost-common'],
    classifiers = [],
)