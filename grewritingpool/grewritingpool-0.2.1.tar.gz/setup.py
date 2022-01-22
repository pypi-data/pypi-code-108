from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='grewritingpool',
    version='0.2.1',
    description='Helper for GRE Writing Pool',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='GPLv3',
    packages=['grewritingpool'],
    author='Patrick Wu',
    author_email='me@patrickwu.space',
    python_requires='>=3.5',
    scripts=['scripts/grewriting','scripts/grewriting.cmd'],
    install_requires=[
          'lxml','beautifulsoup4','requests'
      ],
    keywords=['gre','writing'],
    classifiers=[
        "Environment :: Console",
        "Topic :: Education",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3 :: Only"
    ],
    url='https://github.com/patrick330602/grewritingpool'
)
