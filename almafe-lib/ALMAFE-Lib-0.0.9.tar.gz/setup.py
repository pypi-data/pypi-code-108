import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ALMAFE-Lib",
    version="0.0.9",
    author="Morgan McLeod",
    author_email="mmcleod@nrao.edu",
    description="Contains reusable tools which are required by other ALMAFE packages.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/morganmcleod/ALMAFE-Lib",
    packages=setuptools.find_packages(),
    install_requires=['python-dateutil>=2.8.1',
                      'mysql-connector-python>=8.0.18',
                      'cx-oracle>=8.1.0'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)