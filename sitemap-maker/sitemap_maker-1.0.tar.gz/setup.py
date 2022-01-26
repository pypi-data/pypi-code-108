from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert_file('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='sitemap_maker',
    version='1.0',
    description='Python tool to generate sitemap XML files',
    long_description=long_description,
    author='Gabriel Bordeaux',
    author_email='pypi@gab.lc',
    url='https://github.com/gabfl/sitemap_maker',
    license='MIT',
    packages=['sitemap_maker'],
    package_dir={'sitemap_maker': 'src'},
    install_requires=[  # external dependencies
        'sitecrawl',
        'requests',
        'dateparser==1.1.*',
    ],
    entry_points={
        'console_scripts': [
            'sitemap_maker = sitemap_maker.sitemap:main',
        ],
    },
    classifiers=[  # see https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking',
        'Topic :: Software Development :: Libraries',
        'Topic :: Text Processing :: Markup :: XML',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Natural Language :: English',
        #  'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        #  'Development Status :: 5 - Production/Stable',
    ],
)
