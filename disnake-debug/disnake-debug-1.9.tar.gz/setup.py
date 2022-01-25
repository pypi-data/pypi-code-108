from distutils.core import setup
__version__ = __import__('disnake-debug.__init__').__version__
import pathlib  

ROOT = pathlib.Path(__file__).parent
with open(ROOT / "README.md", "r", encoding="utf-8") as f:
    README = f.read()

setup(
    name="disnake-debug",
    packages=["disnake-debug", "disnake-debug.dialogs"],
    version=__version__,
    license="MIT",
    description="A visual debugging extension for disnake discord bots including easy blacklisting, evaluation, echoing and much more!",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Caeden PH",
    author_email="caedenperelliharris@gmail.com",
    url="https://github.com/CaedenPH/disnake-debug",
    download_url=f'https://github.com/CaedenPH/disnake-debug/archive/refs/tags/v_{__version__.replace(".", "")}.tar.gz',
    keywords=["disnake", "discord", "debugging", "visual", "extension", "cog"],
    project_urls={
        "Code": "https://github.com/CaedenPH/disnake-debug",
    },
    install_requires=["disnake", "aiosqlite", "fuzzywuzzy", "python-Levenshtein"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
