from setuptools import setup, find_packages

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='sampleslicer',
      version='1.0.1',
      description='Graphically slice up 4-dimensional datasets using quaternions.',
      long_description=long_description,
      long_description_content_type="text/x-rst",
      url='https://doi.org/10.5281/zenodo.5523256',
      author='John W',
      license='GPLv3',
      packages=find_packages(),
      package_data={'sampleslicer': ['template/*.py']},
      install_requires=[
        "matplotlib",
        "numpy",
        "numpy-quaternion",
        #numba
        "scipy",
        "imread==0.7.4",
        "psutil==5.8.0"
        ],
      entry_points={
          "console_scripts": [
              "sslice = sampleslicer.cli:main",
          ]
      }
      )
