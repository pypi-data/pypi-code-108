from setuptools import setup, find_packages

version = '0.19'

setup(name='imio.pyutils',
      version=version,
      description="Some python useful methods",
      long_description=open("README.rst").read() + "\n" + open('CHANGES.rst').read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
      ],
      keywords='Python IMIO',
      author='IMIO',
      author_email='support@imio.be',
      url='http://github.com/imio/imio.pyutils/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['imio'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'future',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
