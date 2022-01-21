import setuptools

setuptools.setup(
    name="bda-service-utils",
    version="0.0.1.25",
    author="Alida research team",
    author_email="salvatore.cipolla@eng.it",
    description="Utils for bda services written in python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires = [
        "sqlalchemy>=1.0.12",
    ],

)
