from setuptools import setup

setup(
    entry_points={
        'console_scripts': [
            'datenraffinerie = datenraffinerie.datenraffinerie:cli',
        ]
    },
    install_requires=[
        'Click',
        'luigi',
        'pandas',
        'matplotlib',
        'numpy',
        'scipy',
        'uproot',
        'pyyaml',
        'zmq',
        'pytest',
        'awkward',
        'tables'
    ]
)
