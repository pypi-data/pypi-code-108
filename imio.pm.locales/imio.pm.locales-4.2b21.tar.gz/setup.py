from io import open
from setuptools import setup, find_packages
import os

version = '4.2b21'

setup(name='imio.pm.locales',
      version=version,
      description="Locales for PloneMeeting",
      long_description=open("README.rst", encoding='utf-8').read() + "\n" + open("CHANGES.rst", encoding='utf-8').read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Development Status :: 6 - Mature",
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Zope2",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
        ],
      keywords='plone i18n locale translation PloneMeeting egov communesplone imio plonegov',
      author='Gauthier Bastien',
      author_email='gauthier@imio.be',
      url='https://github.com/IMIO/imio.pm.locales',
      license='GPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['imio', 'imio.pm'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      extras_require={'test': ['plone.app.testing', 'unittest2']},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
