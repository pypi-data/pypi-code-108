from setuptools import setup


with open('README.md', 'rb') as f:
    longdesc = f.read().decode().strip()


setup(
    setup_requires=[
        'setuptools_scm',
    ],

    use_scm_version={
        'write_to': 'ndscope/__version__.py',
    },

    name='ndscope',
    description="Next-generation NDS time series plotting",
    long_description=longdesc,
    long_description_content_type='text/markdown',
    author='Jameson Graef Rollins',
    author_email='jameson.rollins@ligo.org',
    url='https://git.ligo.org/cds/ndscope',
    license='GPL-3.0-or-later',
    classifiers=[
        ('License :: OSI Approved :: '
         'GNU General Public License v3 or later (GPLv3+)'),
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],

    install_requires=[
        'cairosvg',
        'gpstime',
        'h5py',
        'numpy',
        'pyqtgraph',
        'python-dateutil',
        #'nds2-client',
        'pyyaml',
        'QtPy',
        'setproctitle',
    ],

    packages=[
        'ndscope',
        'ndscope.test',
    ],

    package_data={
        'ndscope': ['*.ui'],
        'ndscope.test': ['templates/*'],
    },

    entry_points={
        'console_scripts': [
            'ndscope = ndscope.__main__:main',
            'ndschans = ndscope.channel_select:main',
        ],
    },
)
