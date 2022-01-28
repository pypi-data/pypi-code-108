from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
  name = 'TechfinDataPipeline',
  packages = ['TechfinDataPipeline'],
  version = '0.0.26',
  license='MIT',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author = 'TOTVS Techfin',
  author_email = 'guilherme.spadaccia@totvs.com.br',
  url = 'https://totvstfs.visualstudio.com/Techfin/_git/techfin-ds-golden-data-pipeline',
  keywords = ['TOTVS', 'Techfin', 'Golden Data Parser'],
  install_requires=[
          'pycarol[dataframe]'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',  # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',  # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',  # Again, pick a license
    'Programming Language :: Python :: 3.4',   #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)
