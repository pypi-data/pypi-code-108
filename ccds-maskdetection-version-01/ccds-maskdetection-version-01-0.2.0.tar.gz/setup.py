from setuptools import find_packages, setup

setup(
    name='ccds-maskdetection-version-01',
    packages=find_packages('src'),
    version='0.2.0',
    description='Mask detection',
    author='seema',
    author_email='seema.timmawagol@kabam.ai',
    license='BSD-3',
    package_dir={'': 'src'},
    url='https://github.com/gmyrianthous/example-publish-pypi'
)
