import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fivem-api",
    use_scm_version=True,
    author="Sander Jochems",
    author_email="contact@sanderjochems.com",
    description="A library to query info, players and resources from FiveM server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/Sander0542/fivem-api",
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'aiohttp>=3.8.1'
    ],
    setup_requires=[
        'setuptools_scm'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
