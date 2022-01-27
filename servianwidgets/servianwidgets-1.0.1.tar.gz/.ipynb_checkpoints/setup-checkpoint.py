from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='servianwidgets',
  version='1.0.1',
  description='A simple library providing dataframe feature selection, and sklearn training comparison widgets',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',
  author='Michael Blayney',
  author_email='michael.blayney@servian.com',
  license='MIT',
  classifiers=classifiers,
  keywords='widgets', 
  packages=find_packages(),
  install_requires=['ipywidgets'] 
)