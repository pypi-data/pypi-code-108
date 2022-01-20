from setuptools import setup, find_packages


setup(
    name='example_neil',
    version='0.1',
    license='MIT',
    author="Neil Wimmers",
    author_email='email@example.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/neiltwimmer/wss_testing',
    keywords='example project',
    install_requires=[
          'scikit-learn',
      ],

)
