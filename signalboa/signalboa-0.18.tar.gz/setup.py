from setuptools import setup, find_packages

install_require = [
    'requests'
]

setup(
    name='signalboa',
    description="Connector for SingalBoa user Api",
    license="Brainalyzed",
    author="Thomas Kopetsch",
    author_email='thomas@brainalyzed.com',
    url='https://github.com/brainalyzed/signalboa',
    packages=find_packages(),
    install_requires=install_require,
    keywords='signalboa',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)
