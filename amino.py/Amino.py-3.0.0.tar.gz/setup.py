from setuptools import setup, find_packages

with open("README.md", "r") as stream:
    long_description = stream.read()

setup(
    name = "Amino.py",
    version = "3.0.0",
    url = "https://github.com/Slimakoi/Amino.py",
    download_url = "https://github.com/Slimakoi/Amino.py/tarball/master",
    license = "MIT",
    author = "Slimakoi",
    author_email = "slimeytoficial@gmail.com",
    description = "A library to create Amino bots.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    keywords = [
        "aminoapps",
        "amino-py",
        "amino",
        "amino-bot",
        "narvii",
        "api",
        "python",
        "python3",
        "python3.x",
        "slimakoi",
        "official"
    ],
    install_requires = [
        "setuptools",
        "requests",
        "six",
        "websockets",
        "websocket-client==0.57.0",
        "aiohttp"
    ],
    setup_requires = [
        "wheel"
    ],
    packages = find_packages()
)
