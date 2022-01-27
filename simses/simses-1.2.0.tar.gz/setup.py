from setuptools import setup, find_packages

setup(
    name='simses',
    version='1.2.0',
    description='Simulation for Stationary Storage Systems (SimSES)',
    long_description='Simulation for Stationary Storage Systems (SimSES). SimSES enables a detailed '
                     'simulation and evaluation of stationary energy storage systems with the '
                     'current main focus on lithium-ion batteries, redox-flow batteries and '
                     'hydrogen storage systems.',
    packages=find_packages(),
    include_package_data=True,
    url='https://gitlab.lrz.de/open-ees-ses/simses',
    download_url='https://gitlab.lrz.de/open-ees-ses/simses/-/releases/simses_v120',
    author='Marc Möller, Daniel Kucevic, Nils Collath, Benedikt Tepe, Martin Cornejo, Anupam Parlikar, Stefan Englberger, Holger Hesse',
    author_email='simses.ees@ed.tum.de',
    license='BSD 3-Clause "New" or "Revised" License',
    install_requires=['scipy',
                      'numpy',
                      'numpy_financial',
                      'pandas',
                      'plotly',
                      'matplotlib',
                      'pytest',
                      'pytz'
                      ],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering',
    ],
)
