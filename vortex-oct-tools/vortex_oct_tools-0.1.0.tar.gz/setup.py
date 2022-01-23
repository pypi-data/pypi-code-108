from setuptools import setup, find_packages

setup(
    name='vortex_oct_tools',
    version='0.1.0',

    description='Python Tools for Vortex',
    long_description='A package of Python tools for Vortex, a library for building real-time OCT engines',

    author='Vortex Developers',
    author_email='contact@vortex-oct.dev',

    license='BSD-3',
    url='https://www.vortex-oct.dev/',

    platforms=['any'],

    packages=find_packages('src'),
    package_dir={'': 'src'},

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering'
    ]
)
