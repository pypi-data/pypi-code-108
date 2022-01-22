import setuptools

long_description = open('README.md').read()

setuptools.setup(
    name="danitonapi",
    version="0.0.4",
    author="Daniton999",
    author_email="zombieservers123@gmail.com",
    description="A global Artificial Intelligence Network called Daniton",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Dart2004/DanitonAPI",
    project_urls={
        "Bug Tracker": "https://github.com/Dart2004/DanitonAPI/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)
 
