from setuptools import setup

setup(
    name = 'ampule',
    packages = ['ampule'],
    version = '0.9.5',
    description='Ampule (Automated MatPlotLib) is a minimalistic tool designed for repeated\
non-interactive processing and plotting of tabular data',
    url = 'https://github.com/Toucandy/ampule',
    download_url = 'https://github.com/Toucandy/ampule/archive/v_095.tar.gz',
    license='MIT',
    author = 'Ilya Pershin',
    author_email='pershin2010@gmail.com',
    install_requires = ['matplotlib', 'pandas', 'parse'],
    data_files=[
        ('ampule', ['Makefile', 'ampule_config.mk']),
        ('ampule/figs/py', ['figs/py/poly.py', 'figs/py/hermite.py']),
        ('ampule/dat', ['dat/poly.dat']),
        ('ampule/dat/hermite', [
            'dat/hermite/H_0.dat',
            'dat/hermite/H_1.dat',
            'dat/hermite/H_2.dat',
            'dat/hermite/H_3.dat',
            'dat/hermite/H_4.dat']),
    ],
    keywords = ['matplotlib', 'plotting', 'pandas'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
  ],
)
