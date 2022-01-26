from setuptools import setup, find_packages


def get_version():
    with open("arrlio/__init__.py", "r") as f:
        for line in f.readlines():
            if line.startswith("__version__ = "):
                return line.split("=")[1].strip().strip('"')
    raise Exception("Can't read version")


setup(
    name="arrlio",
    version=get_version(),
    author="Roma Koshel",
    author_email="roma.koshel@gmail.com",
    license="MIT",
    py_modules=["arrlio"],
    packages=find_packages(
        exclude=(
            "docs",
            "examples",
            "tests",
        )
    ),
    include_package_data=True,
    install_requires=[
        "aiormq>=5.2.0",
        "cryptography",
        "pydantic>=1.9.0",
        "yarl",
        "roview",
        "siderpy[hiredis]",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
    ],
)
