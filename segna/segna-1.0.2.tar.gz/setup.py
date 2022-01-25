import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="segna",
    version="1.0.2",
    description="Run Segna pipelines from your Python code!",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://segna.io",

    author="Segna",
    author_email="josh@segna.io",
    license="MIT",
    keywords=['Segna', 'API'],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        'Intended Audience :: Developers',
        "Programming Language :: Python :: 3",
    ],
    packages=["segna"],
    include_package_data=True,
    install_requires=['requests', 'datetime', 'pandas']
)