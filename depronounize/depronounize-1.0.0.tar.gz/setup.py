
from setuptools import setup, find_packages


setup(
    name="depronounize",
    version='1.0.0',
    description="Pronoun replacement module",
    url="https://github.com/NazarTrilisky/PronounReplacement",
    install_requires=["spacy==2.3.2"],
    include_package_data=True,
    zip_safe=False,
    author_email="",
    license="MIT",
    author="Nazar Trilisky",
    packages=find_packages('src'),
    package_dir={'': 'src'}
)

