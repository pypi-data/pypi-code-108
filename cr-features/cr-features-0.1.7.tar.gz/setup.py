from setuptools import find_packages, setup

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='cr-features',
    #packages=find_packages(include=['cr_features', 'eda_explorer']),
    packages=['cr_features', 'cr_features.eda_explorer'],
    #package_dir = {'': 'cr_features'},
    #py_modules = ["helper_functions"],
    version='0.1.7',
    description='A library for calculating features suitable for context recognition',
    author= 'Department of Intelligent Systems, Jožef Stefan Institute',
    author_email="vito.janko@ijs.si",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    install_requires=["biosppy", "hmmlearn", "numpy", "pandas", "PeakUtils", "scikit-learn", "scipy",
                      "tqdm", "PyWavelets"]
)