from setuptools import setup

# reading long description from file
with open('README.md') as file:
    long_description = file.read()


# specify requirements of your package here
REQUIREMENTS = ['docopt==0.6.2']

# some more details
CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Internet',
    'License :: OSI Approved :: GNU Affero General Public License v3',
    'Programming Language :: Python :: 3'
]

# calling the setup function
setup(name='scalegrid-cli',
    version='1.1.0',
    description='ScaleGrid CLI',
    long_description=long_description,
    license='GPL',
    packages=['cli'],
    include_package_data=True,
    classifiers=CLASSIFIERS,
    install_requires=REQUIREMENTS,
    python_requires='>=3',
    keywords='scalegrid database mongo redis mysql postgresql',
    entry_points={
        "console_scripts": [
            "sg-cli=cli.sg:main"
        ]
    }
)
