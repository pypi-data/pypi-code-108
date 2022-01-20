import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

# with open("./requirements.txt", "r") as reqs:
#     requirements = reqs.read()

setuptools.setup(
    name="AIGrammar",
    version="0.0.6",
    author="metric",
    description="AIGrammar Python package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZaruhiNavasardyan/AIGrammar",
    download_url = 'https://github.com/ZaruhiNavasardyan/AIGrammar/archive/refs/tags/V_006.tar.gz',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=['attrs==21.4.0', 'cached-property==1.5.2', 'certifi==2021.10.8', 'charset-normalizer==2.0.10', 'cloudpickle==2.0.0', 'cycler==0.11.0', 'dice-ml==0.7.2', 'fonttools==4.28.5', 'graphviz==0.19.1', 'h5py==3.6.0', 'idna==3.3', 'importlib-metadata==4.10.1', 'importlib-resources==5.4.0', 'Jinja2==3.0.3', 'joblib==1.1.0', 'jsonschema==4.4.0', 'kiwisolver==1.3.2', 'lightgbm==3.3.2', 'littleutils==0.2.2', 'llvmlite==0.38.0', 'lofo-importance==0.3.1', 'MarkupSafe==2.0.1', 'matplotlib==3.5.1', 'numba==0.55.0', 'numpy==1.21.5', 'outdated==0.2.1', 'packaging==21.3', 'pandas==1.3.5', 'pandas-flavor==0.2.0', 'patsy==0.5.2', 'Pillow==9.0.0', 'pingouin==0.5.0', 'pyarrow==6.0.1', 'pyparsing==3.0.6', 'pyrsistent==0.18.1', 'python-dateutil==2.8.2', 'pytz==2021.3', 'requests==2.27.1', 'scikit-learn==1.0.2', 'scipy==1.7.3', 'seaborn==0.11.2', 'shap==0.40.0', 'six==1.16.0', 'slicer==0.0.7', 'statsmodels==0.13.1', 'tabulate==0.8.9', 'threadpoolctl==3.0.0', 'tqdm==4.62.3', 'typing_extensions==4.0.1', 'urllib3==1.26.8', 'xarray==0.20.2', 'zipp==3.7.0'],
)
