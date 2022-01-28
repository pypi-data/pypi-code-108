from datetime import datetime

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    long_description = readme_file.read()

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.read().splitlines()

setup(
    name="PyNyaaTa",
    version=datetime.now().strftime("%Y%m%d%H%M"),
    author="Xéfir Destiny",
    author_email="xefir@crystalyx.net",
    description="π 😼た, Xéfir's personal animes torrent search engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.crystalyx.net/Xefir/PyNyaaTa",
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    entry_points={
        "console_scripts": ["pynyaata=pynyaata:run"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.5",
)
