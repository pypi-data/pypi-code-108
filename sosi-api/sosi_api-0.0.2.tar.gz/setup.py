import setuptools

setuptools.setup(
    name="sosi_api",
    version="0.0.2",
    author="ronny",
    description='A base for creating a python wrapper of a REST API',
    url="https://github.com/ronrest/sosi_api",
    project_urls={
        "Bug Tracker": "https://github.com/ronrest/sosi_api/issues",
        "Documentation": "https://github.com/ronrest/sosi_api/blob/master/README.md",
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8, <4.0",
    packages=setuptools.find_packages(),
    install_requires=[
        'python-dateutil',
        'python-decouple',
        'requests',
    ],
    extras_require={
        'dev': [
            'pip-tools',
            'pylint',
            'pytest',
            'yapf',
        ]
    },
)