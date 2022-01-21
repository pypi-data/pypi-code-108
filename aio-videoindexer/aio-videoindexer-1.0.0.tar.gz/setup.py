import pathlib
from setuptools import setup


CURRENT_PATH = pathlib.Path(__file__).parent
README_TEXT = (CURRENT_PATH / "README.md").read_text()

setup(
    name="aio-videoindexer",
    version="1.0.0",
    description="An async video indexer package for querying Microsoft Media Services Video Indexer in Python.",
    long_description=README_TEXT,
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="azure media services video indexer asyncio aio async sdk",
    url="https://aio-videoindexer.readthedocs.io/en/latest/",
    project_urls={
        "Documentation": "https://aio-videoindexer.readthedocs.io/en/latest/",
        "Source": "https://github.com/Sealjay/aio-videoindexer",
        "Tracker": "https://github.com/Sealjay/aio-videoindexer/issues",
    },
    author="Chris Lloyd-Jones",
    license="MIT",
    packages=["asyncvideoindexer"],
    install_requires=["aiohttp", "aiohttp[speedups]"],
    python_requires="~=3.6",
    zip_safe=False,
)
