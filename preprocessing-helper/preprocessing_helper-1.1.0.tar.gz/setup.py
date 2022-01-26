from distutils.core import setup
import pathlib
import setuptools


HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setuptools.setup(
    name='preprocessing_helper',
    version='1.1.0',
    description="",
    long_description=README,
    packages=setuptools.find_packages(where="src"),
    author="Joshua Spear",
    author_email="josh.spear9@gmail.com",
    long_description_content_type="text/markdown",
    url="",
    license='MIT',
    classifiers=[],
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[]
)