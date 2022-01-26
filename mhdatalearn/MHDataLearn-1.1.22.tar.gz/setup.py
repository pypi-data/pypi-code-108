from setuptools import setup, find_packages
setup(
    author="Kris Bennett, Samuel Nyeko, Kuang Myat wai yan Yan"\
        "Simon Wellesley Miller",
    name = "MHDataLearn",
    version = "1.1.22",
    description = "A package to preprocess raw Mental Health Services Data "\
        "Sets (MHSDS), apply classification machine learning algorithms"\
            "and select the best performing using algorithm metrics",
    packages=find_packages(include=["MHDataLearn", "MHDataLearn.*"]),
    install_requires = [        
        'numpy>=1.14.0',
        'pandas>=1.0.0',
        'matplotlib>=3.2.0',
        'seaborn>=0.9.1',
        'scikit-learn>=0.22.1',
	'pytest>=6.0.0'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)