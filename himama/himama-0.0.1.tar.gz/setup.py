"""
himama: HiMama Downloader
"""
from setuptools import setup, find_packages

VERSION = '0.0.1'

def get_requirements():
    with open('requirements.txt') as requirements:
        for req in requirements:
            req = req.strip()
            if req and not req.startswith('#'):
                yield req

def get_readme():
    with open('README.md') as readme:
        return readme.read()

setup(name='himama',
      version=VERSION,
      description="himama: HiMama Downloader",
      long_description=get_readme(),
      long_description_content_type='text/markdown',
      classifiers=
      [
          'Topic :: Software Development :: Libraries',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
      ],
      keywords='himama playschool daycare offline backup',
      author='Karthik Kumar Viswanathan',
      author_email='karthikkumar@gmail.com',
      url='http://github.com/guilt/himama',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=list(get_requirements()),
     )
