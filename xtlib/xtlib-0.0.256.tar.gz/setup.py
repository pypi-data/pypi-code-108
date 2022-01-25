#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
import platform
import setuptools

# this must be incremented every time we push an update to pypi (but not before)
VERSION ="0.0.256"

# supply contents of our README file as our package's long description
with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    # azure ML SDK
    "azureml-sdk",          # ==1.15.0",
    "azure-batch",          # ==9.0.0",
    "azure-keyvault",       # ==4.1.0",
    "azure-storage-blob==2.1.0",     # without this, azure-storage-blob is changed to 12.8.0 (by ITP?)

    # this k8s is now JIT installed when user submits a K8s job
    #"azureml-contrib-k8s",   # ==0.1.0.15883786",

    # azure-sensitive version 
    # many azure packages require ruamel.yaml to be between 0.17.10 and 0.17.16, but azureml-core 1.33.0 needs ruamel.yaml<=0.17.4
    # we can't win!  for now, use 0.17.4
    "ruamel.yaml==0.17.4",     # yaml support (this version is compatible by azure libraries and XT)

    # other xtlib dependencies
    "arrow==0.14.0",    # avoid annoying warning msgs in 0.14.4, 
    "grpcio>=1.24.3",       # tensorboard requirement
    "rpyc==4.1.2",      # rpyc requires its versions to match (client/remote)
    "watchdog==0.9.0",  # for watching file we want to copy to grok server (watchdog 0.10.0 has setup error)
    "PyYAML>=5.1.0",    # for YAML parser
    "pymongo==3.12.0",  # for talking to SQL (3.12.0 is needed for backwards compatibility with old mongodb (Azure Cosmos) server (wire version 2) 

    "numpy",           # ==1.19.3",    # general use (version requirement from azure libraries)
    #"future",          # temporarily needed by tensorboard
    "hyperopt",         # for bayesian hyperparam searching
    "tensorboard",      # for logging to Tensorboard
    "psutil",           # for querying and killing processes (XT controller)
    "ptvsd",            # for attaching debugger to python processes
    "matplotlib",       # for plotting (exploring their use)
    "seaborn",          # for plotting styles
    "pandas",           # for DataFrame 
    "python-interface", # for specifying provider interface classes
    "paramiko",         # SSH session-level API (fast access to remote box)
    "dnspython",            # for connecting to MongoDB Atlas 
    "pyodbc",               # for talking to sql server

    # XT testing dependencies
    # "torch==1.2.0",
    # "torchvision==0.4.1",
    # "pillow==6.2.0",  

]

if platform.system() == 'Windows':
    # requirements.append('pywin32')  # windows only package
    # requirements.append('pypiwin32')  # windows only package
    pass
elif platform.system() == 'Linux':
    requirements.append('scikit-learn') # required by shap, "azureml-explain-model
    requirements.append('pyasn1>=0.4.6') # linux only package

setuptools.setup(
    # this is the name people will use to "pip install" the package
    name="xtlib",

    version=VERSION, 
    author="Roland Fernandez",
    author_email="rfernand@microsoft.com",
    description="A set of tools for organizing and scaling ML experiments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rfernand2",

    # this is for ITP support (AML Kubernetes)  
    #pip install --upgrade --disable-pip-version-check --extra-index-url https://"azuremlsdktestpypi.azureedge.net/K8s-Compute/D58E86006C65 "azureml_contrib_k8s 
    #"--extra-index-url https://azuremlsdktestpypi.azureedge.net/K8s-Compute/D58E86006C65",
    #dependency_links=[ 'https://azuremlsdktestpypi.azureedge.net/K8s-Compute/D58E86006C65' ],

    # this will find our package "xtlib" by its having an "__init__.py" file
    packages=[
        "xtlib", "xtlib.helpers", "xtlib.hparams", "xtlib.backends", "xtlib.templates", 
        "xtlib/public_certs", "xtlib/demo_files", "xtlib/demo_files/code", "xtlib.storage",
        "xtlib.storage_v1", "xtlib/help_topics/topics", "xtlib/help_topics/internals", "xtlib/psm"
    ],  # setuptools.find_packages(),

    entry_points={
        'console_scripts': ['xt = xtlib.xt_run:main'],
    },

    # normally, only *.py files are included - this forces our YAML file and controller scripts to be included
    package_data={'': ['*.yaml', '*.sh', '*.bat', '*.txt', '*.rst', '*.crt', '*.json']},
    include_package_data=True,

    # the packages that our package is dependent on
    install_requires=requirements,
    extras_require=dict(
        dev=[
            "sphinx",  # for docs
            "sphinx_rtd_theme"  # for docs
        ], ),

    # used to identify the package to various searches
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)