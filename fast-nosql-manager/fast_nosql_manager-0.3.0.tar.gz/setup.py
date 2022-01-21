import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fast_nosql_manager",
    version="0.3.0",
    author="Oscar da Silva",
    author_email="oscarkaka222@gmail.com",
    description="Um pacote simples para realizar operações no mongoDB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OscarSilvaOfficial/fast_nosql_manager",
    packages=setuptools.find_packages(),
    install_requires=[
        'pymongo>=4.0.1',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
