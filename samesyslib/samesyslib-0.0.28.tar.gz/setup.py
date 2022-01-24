import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="samesyslib",
    version="0.0.28",
    author="SameSystem",
    author_email="giedrius.blazys@samesystem.com",
    description="Common libs used by SameSystem Data Science team.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/samesystem-ds/samesyslib",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    install_requires=[
        'ruamel.yaml',
        'sqlalchemy',
        'pandas'
    ],
    python_requires=">=3.7",
)

