import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="pyEVT", 
    version="0.99.30",
    author="Eise Hoekstra and Mark Span (primary developer)",
    author_email="m.m.span@rug.nl",
    description="Package to communicate with RUG developed hardware",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/markspan/pyEVT",
    download_url = 'https://github.com/markspan/pyEVT/dist/pyEVT-0.99.30.tar.gz',
    packages=setuptools.find_packages(),
	include_package_data=True,

	install_requires=[
          'hidapi',
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
		"Intended Audience :: Science/Research",
    ],
    python_requires='>=3.6',
)
