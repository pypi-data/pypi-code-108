import os
from setuptools import setup, find_packages
from typeduck import __version__

readme = os.path.join(os.path.dirname(__file__), 'README.md')
with open(readme, 'rt', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="typeduck",
    version=__version__,
    packages=find_packages(),
    author='Denis Sazonov',
    author_email='den@saz.lt',
    url="https://github.com/den4uk/typeduck",
    license='MIT License',
    python_requires=">=3.8",
    keywords="typing annotations match check compare validate".split(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=True,
)
