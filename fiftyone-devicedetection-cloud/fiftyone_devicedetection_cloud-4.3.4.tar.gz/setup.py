import setuptools
import os
import io

# Read a text file and return the content as a string.
def read(file_name):

    """Read a text file and return the content as a string."""
    try:
        with io.open(
            os.path.join(os.path.dirname(__file__), file_name), encoding="utf-8"
        ) as f:
            return f.read()
    except:
        return ""

setuptools.setup(
    name="fiftyone_devicedetection_cloud",
    version=read("version.txt"),
    author="51Degrees",
	author_email="support@51degrees.com",
    url="https://51degrees.com/",
    description=("The 51Degrees Pipeline API is a generic web request intelligence and data processing solution with the ability to add a range of 51Degrees and/or custom plug ins (Engines). "
    "This project contains 51Degrees Device Detection engines that can be used with the Pipeline API"),
    long_description=read("readme.md"),
    long_description_content_type='text/markdown',
    python_requires='>=3.5',
    packages=["fiftyone_devicedetection_cloud"],
    install_requires=["fiftyone_devicedetection_shared"],
    license="EUPL-1.2",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    include_package_data=True
)
