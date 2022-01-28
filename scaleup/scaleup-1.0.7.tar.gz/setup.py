import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scaleup",                     # This is the name of the package
    version="1.0.7",                        # The initial release version
    author="Scale-up Systems",                     # Full name of the author
    author_email="python.support@scale-up.com",
    description="Python scripting library for Scale-up RunScript Automation",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.6',                # Minimum version requirement of the package
    py_modules=["scaleup"],             # Name of the python package
    install_requires=[ "pywin32"]                     # Install other dependencies if any
)