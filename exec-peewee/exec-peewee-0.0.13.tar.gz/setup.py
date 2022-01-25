import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="exec-peewee",
    author="Supplayer",
    author_email="x254724521@hotmail.com",
    description="Build peewee model class from Mysql.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Supplayer/exec_peewee.git",
    packages=setuptools.find_packages(include=('execpeewee',)),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=['peewee', 'pymysql', 'cryptography'],
    setup_requires=['setuptools_scm'],
    use_scm_version=True
)
