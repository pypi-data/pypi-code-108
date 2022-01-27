import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cli-essentials",
    version="0.0.3",
    author="Daniel Gill",
    description="Python CLI building essentials",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DanGill/cli-essentials",
    py_modules=["CLI", "colors"],
    packages=setuptools.find_packages(),
    keywords="cli-essentials cli essentials simple color colour easy basic",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='~=3.3',
    license="MIT",
)
