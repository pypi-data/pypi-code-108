from setuptools import find_packages, setup

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='sapply',
    version='0.1.9',
    license='MIT',
    author='Joseph Diza',
    author_email='josephm.diza@gmail.com',
    description='Easily apply arbitrary string manipulations on text.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jmdaemon/sapply',
    project_urls={ 'Bug Tracker': 'https://github.com/jmdaemon/sapply/issues', },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6',
    py_modules=['sapply.charmap'],
    install_requires=['wora', 'spacy'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'sapply = sapply.cli:main',
        ],
    },
    test_suite='tests',
)
