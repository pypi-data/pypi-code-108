import setuptools
 
with open("README.md", "r") as fh:
    long_description = fh.read()
 
setuptools.setup(
    name="pyqbclient",
    version="1.0.1",
    author="Jeff MacDonald",
    author_email="jeffmacd@protonmail.com",
    description="Quickbase API client module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['pyqbclient'],
    package_dir={'pyqbclient':'src/pyqbclient'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
    'numpy>=1.21.4',
    'pandas>=1.3.4',
    'requests>=2.26.0',
    'lxml >=4.6.4',
    ]
)