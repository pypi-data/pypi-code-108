import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="niota",
    version="0.7.0",
    author="Numbers Co., Inc",
    author_email="hi@numbersprotocol.io",
    description="Numbers PyOTA Wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/numbersprotocol/niota",
    packages=setuptools.find_packages(),
    license='GPLv3',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "cryptography>=3.4.6",
        "pycryptodome>=3.10.1",
        "python-magic>=0.4.18",
        "pydantic",
        "requests",
    ],
    tests_require=[
        "pytest",
        "pytest-mock",
    ],
    python_requires=">=3.6",
)
