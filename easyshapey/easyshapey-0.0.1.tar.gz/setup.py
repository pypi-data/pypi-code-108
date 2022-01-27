import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="easyshapey",
    version="0.0.1",
    author="caganze",
    author_email="caganze@gmail.com",
    description=" package to draw boxes in 2d plots",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/caganze/easyshapey",
    packages=setuptools.find_packages(exclude=['docs','tests'], include=['easyshapey']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"]
)