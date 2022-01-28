from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
    
setup(
    name="syglass",
    version="0.55",
    description="syGlass Python API",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author="syGlass",
    author_email="info@syglass.io",
    url="https://syglass.io",
    python_requires=">=3.4.*",
    install_requires=['numpy'],
    packages=['syglass'],
    package_data={
        '': ['*.dll', '*.pyd'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Win32 (MS Windows)'
    ]
)


