from setuptools import setup, find_packages

VERSION = "1.0.0"

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
		name="laundrify_aio", 
		version=VERSION,
		author="Mike Mülhaupt",
		author_email="mike@laundrify.de",
		license="MIT",
    url="https://github.com/laundrify/laundrify-pypi",
		description="A Python package to communicate with the laundrify API",
		long_description=long_description,
		long_description_content_type="text/markdown",
		packages=find_packages(),
		install_requires=["aiohttp"],        
		keywords=["home-assistant", "laundrify"],
		classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
				"Intended Audience :: Developers"
    ],
)