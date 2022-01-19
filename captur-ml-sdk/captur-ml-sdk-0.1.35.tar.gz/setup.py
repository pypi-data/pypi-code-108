from setuptools import setup, find_packages

long_desc = open("README.md").read()
required = ['pydantic']

setup(
    name='captur-ml-sdk',
    version='0.1.35',
    description='The internal Captur Machine Learning SDK',
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url='https://github.com/Captur/captur-ml-sdk',
    author=[
        'Jack Barnett Leveson',
        'Jonny Jackson'
    ],
    author_email='jack@capturphotos.com',
    license='Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International',
    packages=find_packages(exclude=("test",)),
    install_requires=required,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires=">=3.7"
)
