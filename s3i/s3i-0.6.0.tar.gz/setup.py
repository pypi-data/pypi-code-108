import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

# with open("requirements.txt", "r") as req:
#     requirements = req.read()

setuptools.setup(
    name='s3i',
    version='0.6.0',
    author="Kompetenzzentrum Wald und Holz 4.0",
    author_email="s3i@kwh40.de",
    description="S3I Basic functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.kwh40.de/",
    # packages=setuptools.find_packages(where='s3i'),
    packages=setuptools.find_packages(),
    # package_dir={'': 's3i'},
    install_requires=["alabaster>=0.7.12",
                      "astroid>=2.3.3",
                      "certifi>=2019.11.28",
                      "cffi>=1.13.2",
                      "chardet>=3.0.4",
                      "colorama>=0.4.3",
                      "cryptography==3.1",
                      "idna>=2.8",
                      "isort>=4.3.21",
                      "jsonschema>=3.2.0",
                      "Jinja2>=3.0",
                      "lazy-object-proxy>=1.4.3",
                      "MarkupSafe>=1.1.1",
                      "mccabe>=0.6.1",
                      "pika>=1.2.0",
                      "pockets>=0.9.1",
                      "pycparser>=2.19",
                      "Pygments>=2.5.2",
                      "PyJWT==1.6.1",
                      "python-benedict>=0.21.0",
                      "pyparsing>=2.4.5",
                      "pytz>=2019.3",
                      "pyrql>=0.6.0",
                      "requests>=2.26.0",
                      "six>=1.13.0",
                      "snowballstemmer>=2.0.0",
                      "typed-ast>=1.4.0",
                      "urllib3>=1.25.7",
                      "wrapt>=1.11.2",
                      "pgpy",
                      "python-gnupg",
                      "websocket-client",
                      "schema>=0.7.1",
                      "pynput"
                      ],
    classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
         "Operating System :: OS Independent",
    ],
)
