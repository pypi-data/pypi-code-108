import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="restify-ENGYAK",  # Replace with your own username
    version="0.2.5",
    author="Nicholas Schmidt",
    author_email="nick.schmidt3@gmail.com",
    description="Abstractions should save typing, not thinking! This project will provide a quick and simple CLI for REST API consumption. Build your own library of known API endpoints/modifiers, and consume directly via the CLI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ngschmidt/python-resttool",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
