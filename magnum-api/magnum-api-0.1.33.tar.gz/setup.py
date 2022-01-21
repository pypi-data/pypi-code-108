import setuptools
import io
import re

with io.open("magnumapi/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

with open("README.md", "r") as fh:
    long_description = fh.read()

REQUIREMENTS: dict = {
    'core': [
        'numpy',
        'pandas',
        'scikit-optimize',
        'matplotlib',
        'sklearn',
        'IPython',
        'ipywidgets',
        'plotly',
        'coverage',
        'dataclasses',
        'ipyaggrid'],
    'test': [
        'pytest',
        'tox',
        'sphinx',
        'sphinx-rtd-theme'
    ],
    'dev': [
        # 'requirement-for-development-purposes-only',
    ],
    'doc': [
        'sphinx',
        'sphinx-glpi-theme',
        'sphinx-autoapi',
        'sphinxcontrib.napoleon',
        'sphinx-autodoc-typehints',
    ],
}

setuptools.setup(
    name="magnum-api",
    version=version,
    author="ETHZ D-ITET IEF",
    author_email="mmaciejewski@ethz.ch",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.ethz.ch/magnum/magnum-api",
    include_package_data=True,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIREMENTS['core'],
    extras_require={
        **REQUIREMENTS,
        # The 'dev' extra is the union of 'test' and 'doc', with an option
        # to have explicit development dependencies listed.
        'dev': [req
                for extra in ['dev', 'test', 'doc']
                for req in REQUIREMENTS.get(extra, [])],
        # The 'all' extra is the union of all requirements.
        'all': [req for reqs in REQUIREMENTS.values() for req in reqs],
    },

)
