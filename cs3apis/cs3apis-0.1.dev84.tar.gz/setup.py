import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cs3apis",
    use_scm_version={
      "local_scheme": "no-local-version"
    },
    setup_requires=['setuptools_scm'],
    author="CS3 Organization",
    author_email="contact@cs3community.org",
    description="CS3 API client for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cs3org/python-cs3apis",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
