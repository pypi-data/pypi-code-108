from setuptools import setup

with open("README.md","r") as fh:
    long_description = fh.read()

setup(
    name='pycogent',
    version='0.0.2',
    description='Post-processing tools for COGENT plasma simulation code',
    py_modules=["pycogent"],
    package_dir={'':'src'},
    setup_requires=["numpy"],                        # Just numpy here
    install_requires=["matplotlib","numpy","h5py"],   # Add any of your other dependencies here
    classifiers=[
                "Programming Language :: Python :: 3",
                "License :: OSI Approved :: MIT License",
                "Operating System :: OS Independent"
                ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    extras_require={
        "dev": [
            "pytest >= 3.7"
        ]
    },
    url="https://github.com/arknyazev/pycogent",
    author_email="aknyazev@ucsd.edu",
    author="Alex Knyazev"
)
