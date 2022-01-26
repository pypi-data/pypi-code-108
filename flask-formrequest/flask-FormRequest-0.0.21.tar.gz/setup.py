import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flask-FormRequest",
    version="0.0.21",
    author="edcilo",
    description="Request validator for flask",
    long_description=long_description,
    long_description_content_type="text/markdown",
    exclude=["test"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    include_package_data=True,
    packages=['flaskFormRequest', 'flaskFormRequest.filters', 'flaskFormRequest.validators'],
    package_dir={'':'src'},
    install_requires=[
        'email-validator==1.1.3',
    ],
)
