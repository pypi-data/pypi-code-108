from distutils.core import setup


from setuptools import setup

# read the contents of your README file
from os import path

try:
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()
except:
    with open('README.md', 'r') as f:
        long_description = f.read()


setup(
    name='gb-dl',
    version='1.7.40',
    scripts=['gb-dl.py'],

    url='https://github.com/barakagb/gb-dl',
    classifiers=[
     
      'Programming Language :: Python :: 3.6',
      'Programming Language :: Python :: 3.8',
       'Programming Language :: Python :: 3.9',
    ],
    keywords='infosec4tc stackskills -dl ehacking -dl teachable -dl coding with mosh academy-dl designerup gb-dl course downloader dl howto download teachle courses',
    python_requires='>=3.6',
    install_requires=[
          'requests',
	  'unidecode',
          'beautifulsoup4',
          'youtube-dl',
          'lxml',
          'lz4',
          'wget',
	  'cloudscraper',
      ],

    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    author='barakagb',
    author_email='barakagb@gmail.com',
    description='A python based utility to download courses from infosec4tc.teachable.com ,ehacking.net ,stackskills.com and designerup.co ...etc for personal offline use.',
    include_package_data=True,
    zip_safe=False
)

