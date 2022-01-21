import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
    
def _requires_from_file(filename):
    return open(filename, encoding="utf8").read().splitlines()

packages = [
    "discord_api_types"
]

extras = {
    "speed": [
        "ujson>=1.35",
        "uvloop>=0.5.3"
    ]
}

setuptools.setup(
    project_urls = {
        "Documentation": "https://discord-api-py-org.github.io/document/"
    },
    extras_require=extras,
    packages=packages,
    name="discord-api-types",
    version="0.0.3",
    author="DMS",
    author_email="masato190411@gmail.com",
    description="This is discord-api low wrapper.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/discord-api-py-org/discord-api-types",
    install_requires=_requires_from_file('rqs.txt'),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
