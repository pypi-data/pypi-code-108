from setuptools import setup


with open('README.md', 'rb') as f:
    longdesc = f.read().decode().strip()


setup(
    setup_requires=[
        'setuptools_scm',
    ],

    name='gpstime',
    description='GPS-aware datetime module',
    long_description=longdesc,
    long_description_content_type='text/markdown',
    author='Jameson Graef Rollins',
    author_email='jameson.rollins@ligo.org',
    url='https://git.ligo.org/cds/gpstime',
    license='GPL-3.0-or-later',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        ('License :: OSI Approved :: '
         'GNU General Public License v3 or later (GPLv3+)'),
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    packages=[
        'gpstime',
    ],

    tests_require=[
        'python-dateutil',
    ],
    test_suite='gpstime.test',

    install_requires=[
        'python-dateutil',
        'requests',
    ],

    # entry_points={
    #     'console_scripts': [
    #         'gpstime = gpstime.__main__:main',
    #     ],
    # },
    scripts=[
        'bin/gpstime',
    ],
)
