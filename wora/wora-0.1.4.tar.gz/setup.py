from setuptools import find_packages, setup

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='wora',
    version='0.1.4',
    license='GPLv3',
    author='Joseph Diza',
    author_email='josephm.diza@gmail.com',
    description='Write once, run anywhere, a python library with general purpose utilities.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jmdaemon/wora',
    project_urls={ 'Bug Tracker': 'https://github.com/jmdaemon/wora/issues', },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6',
    py_modules=['wora.file', 'wora.dynmod'],
    install_requires=[],
    include_package_data=True,
    zip_safe=False,
    test_suite='tests',
)
