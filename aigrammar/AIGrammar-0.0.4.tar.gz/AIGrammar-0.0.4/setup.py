import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as reqs:
    requirements = reqs.read()

setuptools.setup(
    name="AIGrammar",
    version="0.0.4",
    author="metric",
    description="AIGrammar Python package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZaruhiNavasardyan/AIGrammar",
    download_url = 'https://github.com/ZaruhiNavasardyan/AIGrammar/archive/refs/tags/V_004.tar.gz',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[requirements],
)
