import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ANTConnect", # Replace with your own username
    version="2022.3.1",
    author="ANT CDE",
    author_email="info@antcde.io",
    description="Python SDK for ANT Common Data Engineering",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://antcde.io",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['requests']
)
