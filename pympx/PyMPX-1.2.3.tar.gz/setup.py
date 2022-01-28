from setuptools import setup, find_packages

exec(open('pympx/version.py').read())

with open("README.rst", "r") as fh:
    long_description = fh.read()

        
#Update the Trove classifiers (see https://pypi.org/pypi?%3Aaction=list_classifiers) based version being alpha/beta or production
development_status = "5 - Production/Stable"

if "alpha" in __version__.lower():
    development_status = "3 - Alpha"
if "beta" in __version__.lower():
    development_status = "4 - Beta"


    
setup(
    name="PyMPX",
    version=__version__,
    packages=['pympx'],
    author="Metapraxis Ltd.",
    author_email="pympx@metapraxis.com",
    maintainer="Jonathan Adrian Treloar",
    description="Metapraxis Empower python API",
    license='MIT License',
    license_file='LICENSE.txt',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    project_urls={"Documentation":"https://api.metapraxis.com"},
    include_package_data=True,
    package_data={
        # If pympx contains *.eimp files, include them:
        'pympx': ['importer_scripts/*.eimp'],
        '': ['license.txt'],
    },
    eager_resources=['pympx/importer_scripts/*.eimp'],  # tell distutils where the importer scripts distributed with this package are kept
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: {}".format(development_status),
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Office/Business :: Financial"
    ],
    install_requires=[
               'pywin32',
               'cryptography',
               'pandas'
    ],
    python_requires='>=3',
    zip_safe=False,
)

