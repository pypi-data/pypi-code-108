from setuptools import setup
from basix import __version__

with open("README.md", "r") as fh:
    readme = fh.read()

setup(
    name="basix",
    version=__version__,
    # url="",
    license="MIT License",
    author="Eduardo M. de Morais",
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email="emdemor415@gmail.com",
    keywords="",
    description=u"Utils for python",
    packages=["basix"],
    install_requires=["numpy", "scipy", "pandas", "setuptools", "tqdm", "scikit-learn"],
)
