from setuptools import setup, find_packages

with open('README.rst') as README:
    long_description = README.read()
    description = long_description[
        :long_description.index('Description')].split("*")[1].strip()
    long_description = long_description[long_description.index('Description'):]

version = {}
with open("a2p2/version.py") as fp:
    exec(fp.read(), version)

setup(
    name='a2p2',
    version=version['__version__'],
    python_requires='>=3',
    description=description,
    long_description=long_description,
    #      install_requires=['astropy', 'p2api','pygtk'],
    # PyGtk is not working on some linux
    # anaconda also fails
    # prefere the use of your default python packages on your linux
    # what is the solution for mac ?
    # we continue moving tk as first gui backend
    # install_requires=['astropy', 'p2api', 'python-tk'] + (['pygtk'] if
    # platform.startswith("win") else []),
    install_requires=['astropy>=4.3.1', 'p2api', 'appdirs'],
    url='http://www.jmmc.fr/a2p2',
    author='JMMC Tech Group',
    author_email='jmmc-tech-group@jmmc.fr',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
#        'Programming Language :: Python :: 2',
#        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    license='OSI Approved :: GNU General Public License v3 (GPLv3)',
    packages=find_packages(),
    include_package_data=True,
    entry_points={'console_scripts': ['a2p2=a2p2.__main__:main']},
    keywords='observation preparation tool optical-interferometry p2 samp'
)
