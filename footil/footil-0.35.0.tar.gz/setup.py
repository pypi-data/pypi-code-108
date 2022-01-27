from distutils.core import setup

from footil import __version__

test_deps = [
    "pytest",
    "mock",
]

extras = {
    'test': test_deps,
}

setup(
    name='footil',
    version=__version__,
    packages=['footil', 'footil.tools'],
    license='LGPLv3',
    url='https://github.com/focusate/footil',
    description="Various Python helpers for other projects",
    long_description=open('README.rst').read(),
    install_requires=[
        'yattag',
        'python-dateutil',
        'verboselogs',
        # TODO: upgrade to 3.*.* >= version once it is released.
        'semver <= 2.13.0',
        'natsort',
    ],
    tests_require=test_deps,
    extras_require=extras,
    maintainer='Andrius Laukavičius',
    maintainer_email='dev@focusate.eu',
    python_requires='>=3.5',
    classifiers=[
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
)
