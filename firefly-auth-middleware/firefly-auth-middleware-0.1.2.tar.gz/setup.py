import setuptools
from setuptools.command.develop import develop
from setuptools.command.install import install


setuptools.setup(
    name='firefly-auth-middleware',
    version='0.1.2',
    author="",
    author_email="",
    description="Put project description here.",
    long_description="Long description here.",
    url="",
    entry_points={
        'console_scripts': ['firefly=firefly.presentation.cli:main']
    },
    install_requires=[
        'firefly-dependency-injection>=0.1',
    ],
    packages=setuptools.PEP420PackageFinder.find('src'),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ]
)
