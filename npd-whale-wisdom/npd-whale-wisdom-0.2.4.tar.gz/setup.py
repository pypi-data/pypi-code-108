import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="npd-whale-wisdom",
    version="0.2.4",
    author="Max Leonard",
    author_email="maxhleonard@gmail.com",
    description="Library for making use of Whale Wisdom API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://NPDGroup@dev.azure.com/NPDGroup/NPDFinancialServices/_git/WhaleWisdom",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src","WhaleWisdom":"src/WhaleWisdom"},
    packages=["WhaleWisdom","WhaleWisdom.Common","WhaleWisdom.FundHoldings"],
    python_requires=">=3.6",
    install_requires = [
        "pandas",
        "XlsxWriter",
        "certifi",
        "requests",
        "beautifulsoup4",
        "matplotlib"
    ]
)