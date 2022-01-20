from setuptools import setup

setup(
    entry_points={
        'console_scripts': [
            'datenraffinerie = datenraffinerie.datenraffinerie:cli',
        ]
    },
    install_requires=[
        'Click',
        'luigi==3.0.3',
        'pandas==1.3.5',
        'matplotlib',
        'numpy',
        'scipy',
        'uproot',
        'pyyaml',
        'zmq',
        'pytest',
    ]
)
