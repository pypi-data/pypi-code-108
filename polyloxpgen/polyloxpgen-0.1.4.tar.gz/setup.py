
from setuptools import setup
from setuptools import find_packages

setup(
      name='polyloxpgen',
      version='0.1.4',
      description='Barcode purging and pgen (probability of generation) calculation for Polylox data.',
      url='https://github.com/mauricelanghinrichs/polyloxpgen',
      author='Maurice Langhinrichs',
      author_email='m.langhinrichs@icloud.de',
      license='MIT',

      # README is rst currently, switch to md / markdown for pypi:
      # long_description_content_type="text/markdown"
      long_description_content_type="text/x-rst",
      long_description="Please visit polyloxpgen on `GitHub <https://github.com/mauricelanghinrichs/polyloxpgen>`_.",

      # further required package data is specified via MANIFEST (for whl and tar builds)
      include_package_data=True,
      packages=find_packages(exclude=('tests', 'tests.original', 'tests.temp')),

      install_requires=['numpy>=1.17.3', 'pandas>=1.1.0'],

      test_suite='tests',
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      python_requires='>=3.6',

      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
        ],
      )
