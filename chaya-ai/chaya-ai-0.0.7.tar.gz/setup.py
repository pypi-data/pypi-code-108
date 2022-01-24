from setuptools import setup, find_packages

VERSION = '0.0.7'
DESCRIPTION = 'chaya-ai'
LONG_DESCRIPTION = 'chaya-ai sdk package. \n Chaya takes care of tracking model lineage and project assets, so you can focus on development. \n With Chaya auto-versioning, you can power through model training, and record every step along the way.'

# Setting up
setup(
    # the name must match the folder name ''
    name="chaya-ai",
    version=VERSION,
    author="Chaya-ML Dev",
    author_email="<sundi@chaya.ai>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    include_package_data=True,
    install_requires=['aiohttp','asyncio','requests','pybase64','dbutils','iplotter','tabulate','pandas'],
    keywords=['python', 'chaya-ai'],
    license='MIT',
    url = 'https://app.chaya.ai/',
    download_url = 'https://storage.googleapis.com/chaya-assets/chaya_ai-0.0.4.tar.gz',
    classifiers= [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)