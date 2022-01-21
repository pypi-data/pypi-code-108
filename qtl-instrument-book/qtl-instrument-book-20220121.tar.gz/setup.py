from pathlib import Path
from setuptools import setup, find_packages


here = Path(__file__).resolve().parent
long_description = here.joinpath('readme.md').read_text(encoding='utf-8')


setup(
    name='qtl-instrument-book',
    version='20220121',
    description='Quantalon Instrument Book',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.9.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'toml',
    ]
)
