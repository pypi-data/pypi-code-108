from setuptools import (
    find_packages,
    setup
)

INSTALL_REQUIRES = (
    'cached_property',
    'requests',
    'pandas'
)

setup(
    name='property_price_register',
    version='0.0.8',
    python_requires='>=3.6',
    author='Robert Lucey',
    url='https://github.com/RobertLucey/property-price-register',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=INSTALL_REQUIRES,
    package_data={
        'property_price_register': [
            'resources/PPR.csv.tar.gz',
        ]
    },
    entry_points={
        'console_scripts': [
            'load_property_price_register = property_price_register.bin.load:main',
        ]
    }
)
