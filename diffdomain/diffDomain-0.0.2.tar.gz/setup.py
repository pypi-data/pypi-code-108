import setuptools

with open('README.rst','r') as fh:
    long_description = fh.read()
    
setuptools.setup(
    name = 'diffDomain',
    version = '0.0.2',
    author = 'Dechao Tian',
    author_email = 'tiandch@mail.sysu.edu.cn',
    description = 'DiffDomain can test the significant difference of TADs.',
    long_description = long_description,
    url = 'https://github.com/Tian-Dechao/diffDomain',
    packages = setuptools.find_packages(),
    install_requires=['hic-straw==0.0.6',
                     'TracyWidom==0.3.0',
                      'pandas==0.18.1',
                      'numpy==1.15.0',
                      'docopt==0.6.2',
                      'matplotlib==1.5.1',
                      'statsmodels==0.6.1'
                     ],
    classifiers = [
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
    
    




)