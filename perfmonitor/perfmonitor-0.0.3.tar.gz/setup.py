# from distutils.core import setup
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name='perfmonitor',
    version='0.0.3',
    license='MIT',
    description='Performance monitor CLI for Windows: parse and display performance counter from \'psutil\' and \'nvidia-smi\'.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Lorenzo Bonicelli',
    author_email='loribonna@gmail.com',
    url='https://github.com/loribonna/PerfMonitorCLI',
    download_url='https://github.com/loribonna/PerfMonitorCLI/archive/refs/tags/v0.0.3.zip',
    keywords=['performance', 'monitor', 'windows', 'cli', 'powershell', 'commandline', 'htop'],
    packages=find_packages(),
    entry_points='''
        [console_scripts]
        perfmonitor=perfmonitor.main:run
    ''',
    install_requires=[requirements],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
