from setuptools import setup, find_packages


setup(
    name='broker_clients',
    version='0.2.1',
    license='UNLICENSED',
    author="Oswaldo Cruz",
    author_email='oswaldo_cs_94@hotmail.com',
    url='https://github.com/gmyrianthous/example-publish-pypi',
    keywords='example project',
    entry_points={
        'console_scripts': ['account_manager=broker_clients.binance_proxy.broker.account_manager:command'],
    },
    packages=['broker_clients'],
    package_data={
        '': [
            'alembic/*',
            'data/*',
            'alembic/versions/*',
            'emulator_proxy/*/*.py',
            'emulator_proxy/*.py',
            'quantfury_proxy/*/*.py',
            'quantfury_proxy/*.py',
            'binance_proxy/*/*.py',
            'binance_proxy/*.py'
        ],
    }
)