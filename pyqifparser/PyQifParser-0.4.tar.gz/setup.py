from setuptools import setup

setup(name='PyQifParser',
      version='0.4',
      description='A(nother) Python-based Parser for Quicken / Lexware Finance Manager QIF files.',
      url='https://github.com/hhessel/PyQIF-Parser',
      author='Uwe Ziegenhagen / Packaged by Henrik Hessel',
      author_email='hhessel@web.de',
      license='MIT',
      packages=['PyQifParser'],
      python_requires=">=3.6",
      install_requires=[
       "pandas", "numpy"
      ],
      zip_safe=False)