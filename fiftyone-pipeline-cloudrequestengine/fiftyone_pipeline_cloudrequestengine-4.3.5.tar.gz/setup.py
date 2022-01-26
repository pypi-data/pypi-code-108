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
    name="fiftyone_pipeline_cloudrequestengine",
    version=read("version.txt"),
    author="51Degrees",
    author_email="support@51degrees.com",
    url="https://51degrees.com/",
    description=("The 51Degrees Pipeline API is a generic web request intelligence and data processing solution with the ability to add a range of 51Degrees and/or custom plug ins (Engines). "
    "This package extends the flow element class created by the fiftyone-pipeline-core package into a specialized type of flow element called an engine."),
    long_description=read("readme.md"),
    long_description_content_type='text/markdown',
    python_requires='>=3.5',
    packages=["fiftyone_pipeline_cloudrequestengine"],
    install_requires=[
          'fiftyone_pipeline_engines',
          'requests',
    ],
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
