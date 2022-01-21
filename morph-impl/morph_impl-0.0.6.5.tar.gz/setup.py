import setuptools


with open('README.md') as f:
    README = f.read()

setuptools.setup(
    author="Jared Lutgen",
    author_email="jlutgen@morpheusdata.com",
    name='morph_impl',
    license="MIT",
    description='morph_impl is a python package to help implement MorpheusData platform. ',
    version='v0.0.6.5',
    long_description=README,
    url='https://gitlab.com/jaredlutgen/morpheus-implementation.git',
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    install_requires=[
        'requests',
        'pillow',
        'PyYAML',
        'tqdm',
        'cerberus'
        ],
    classifiers=[
        # Trove classifiers
        # (https://pypi.python.org/pypi?%3Aaction=list_classifiers)
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
    ],
)
