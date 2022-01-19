import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt', 'r') as rf:
    requirements = rf.read().splitlines()

setuptools.setup(
    name="anatools",
    version='1.0.12',
    author="Rendered AI, Inc",
    author_email="admin@rendered.ai",
    description="Tools for development with the Rendered.ai Platform.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://rendered.ai",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
)
