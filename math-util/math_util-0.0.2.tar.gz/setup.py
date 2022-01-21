from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='math_util',
    version='0.0.2',
    description='The math-utility module makes it simple for you to do number manipulation and perform various operations on numbers.',
    py_modules=["math_util"],
    package_dir={'': 'src'},
    extras_require={
        "dev": [
            "pytest >= 3.7",
            "check-manifest",
            "twine"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="R K",
    author_email="ravinderkunta68@gmail.com",
    url="https://github.com/kunta-ravinder/math-util"
)