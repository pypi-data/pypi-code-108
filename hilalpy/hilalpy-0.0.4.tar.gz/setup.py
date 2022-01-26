import setuptools

with open("README.txt", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hilalpy", # Replace with your own username
    version="0.0.4",
    author="waned",
    author_email="msyazwanfaid@gmail.com",
    description="A package to analyse the data of Moon Sighting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/msyazwanfaid/hilalpy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)