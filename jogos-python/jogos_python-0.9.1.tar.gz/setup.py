import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="jogos_python",
    version="0.9.1",
    description="Facilita a criação de jogos com Python",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://jogos-python.readthedocs.io",
    author="LIpE/UFRJ",
    author_email="lipe@poli.ufrj.br",
    packages=["jogos_python"],
    include_package_data=True,
    install_requires=["pygame"],
)