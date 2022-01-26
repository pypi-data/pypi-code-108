from setuptools import setup, find_packages
setup(

    name = "MHDataLearn",
    version = "1.1.2",
    descriptions = "",
    packages=find_packages(include=["MHDataLearn", "MHDataLearn.*"]),

    install_requires = [        
        'numpy>=1.14.0',
        'pandas>=1.0.0',
        'matplotlib>=3.2.0',
        'seaborn>=0.9.1',
        'scikit-learn>=0.22.1'
    ],
)