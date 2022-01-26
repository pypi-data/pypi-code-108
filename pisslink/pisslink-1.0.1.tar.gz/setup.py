from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='pisslink',
    author='KaasToast',
    url='https://github.com/BigCord-py/Pisslink',
    version='V1.0.1',
    packages=['pisslink'],
    license='MIT',
    description='Minimalistic lavalink wrapper based on wavelink. Made for Pycord.',
    include_package_data=True,
    install_requires="aiohttp>=3.6.0,<3.9.0"
)