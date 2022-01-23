from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='cleanedtext',
  version='0.0.1',
  description='A very basic python library through which  you can clean your text ',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Madhura D Bhalke',
  author_email='madhurabhalke13@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='cleanedtext', 
  packages=find_packages(),
  install_requires=[''] 
)