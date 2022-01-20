# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='bifs',
    description='Bayesian Imaging in Fourier Space (BIFS)',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='John Kornak, Karl Young, Ross Boylan',
    author_email='john.kornak@ucsf.edu,kyoung21b2000@gmail.com',
    maintainer_email='ross.boylan@ucsf.edu,bifs@ucsf.edu',
    url='https://github.com/ucsf-deb/bifs',
    license=license,
    packages=['bifs'],
    include_package_data=True,
    # current documentation only gives the setup.cfg syntax for entry points
    # and the translation is not obvious.  Used https://stackoverflow.com/questions/774824/explain-python-entry-points
    entry_points = {
        "gui_scripts" : ["bifs_gui = bifs.bifs_gui:launch"]
        },

    # remember to keep in sync with requirements.txt
    # nibabel is only necessary if your image format requires it
    install_requires=['imageio',
                      'jsonpickle',
                      'matplotlib',
                      'nibabel',
                      'numpy >= 1.17',
                      'PyQt5',
                      'scipy'],
    # not extras_requireS
    extras_require={"NI" : "nibabel",
                    "tests" : "pytest"},

    # license type TBD
    classifiers = ['Programming Language :: Python :: 3',
                   'Development Status :: 4 - Beta',
                   'Intended Audience :: Science/Research',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Topic :: Multimedia :: Graphics',
                   'Topic :: Scientific/Engineering :: Image Processing',
                   'Topic :: Scientific/Engineering :: Visualization',
                   ]
)

