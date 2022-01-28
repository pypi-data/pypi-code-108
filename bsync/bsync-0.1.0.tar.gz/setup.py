from setuptools import setup


with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='bsync',
    version='0.1.0',
    author='Justin Quick',
    author_email='jquick@stsci.edu',
    url='https://github.com/spacetelescope/bsync',
    license='APACHE 2',
    license_files=('LICENSE',),
    description='Sync files from your computer to Box.com using the Box API. Think rsync for Box.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.5',
    project_urls={
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Environment :: Console',
    ],
    package_data={

    },
    packages=['bsync'],
    install_requires=[
        'boxsdk[jwt]',
        'click',
        'progress',
    ],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'bsync=bsync.cli:bsync',
        ]
    }
)
