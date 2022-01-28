from ast import AnnAssign
from setuptools import setup, find_packages


LONGDESCRIPTION = open('README.md').read()

VERSION = "0.0.2"
DESCRIPTION = "A Python module for colorizing text in Discord using ANSI color codes."

# Setting up
setup(
    name="discord_colorize",
    version=VERSION,
    author="TheOnlyWayUp",
    author_email="thedarkdraconian@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONGDESCRIPTION,
    packages=find_packages(),
    install_requires=["asyncio", "aiohttp"],
    keywords=[
        "discord",
        "discord.py",
        "codeblocks",
        "selfbot",
        "ANSI",
        "colored text"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
