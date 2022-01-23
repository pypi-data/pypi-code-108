from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Developers',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
setup(
  name='byteworker',
  version='1.0.2',
  description='Working with byte made easy',
  long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
  long_description_content_type='text/markdown',
  url='https://himelrana.com',  
  author='Himel',
  author_email='contact@himelrana.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='byte to word to decimal', 
  packages=find_packages(),
  install_requires=[''] 
)
