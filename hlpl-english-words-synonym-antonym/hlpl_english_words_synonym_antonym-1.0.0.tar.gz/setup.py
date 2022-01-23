#! /usr/bin/python
from setuptools  import setup
import os
import sys
import platform
import configparser

from io import open
# to install type:
# python setup.py install --root=/
LONG_DESCRIPTION=open('README.md','r',encoding='utf8').read()        
        
if sys.version_info[0] < 3:
    raise Exception(
        'You are tying to install hlpl_english_words_synonym_antonym on Python version {}.\n'
        'Please install hlpl_english_words_synonym_antonym in Python 3 instead.'.format(
            platform.python_version()
        )
    )
    
config = configparser.ConfigParser()
current_directory = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(current_directory, 'hlpl_english_words_synonym_antonym/setup.cfg')
config.read(config_file_path)

VERSION = config['hlpl_english_words_synonym_antonym']['version']
AUTHOR = config['hlpl_english_words_synonym_antonym']['author']
AUTHOR_EMAIL = config['hlpl_english_words_synonym_antonym']['email']
URL = config['hlpl_english_words_synonym_antonym']['url']


projects_urls={}
for i in range(4,len(list(config['hlpl_english_words_synonym_antonym'].keys()))):
    x=list(config['hlpl_english_words_synonym_antonym'].keys())[i]
    y=x
    if i>3:
       y=y[0:len(y)-4]
    projects_urls[y]=config['hlpl_english_words_synonym_antonym'][x]
    

setup (name='hlpl_english_words_synonym_antonym', version=VERSION,
      description='hlpl_english_words_synonym_antonym lists english words synonyms and antonyms in readable database python package',
      long_description_content_type='text/markdown',  
      long_description = LONG_DESCRIPTION,       
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      download_url=URL+'/download/',
      project_urls=projects_urls,      
      python_requires='>=3, <=3.9',
      license='MIT',
      platform="OS independent",
      keywords=['hlpl_english_words_synonym_antonym', 'hlpl english words synonym antonym', 'english words synonym antonym', 'hlpl english words synonym antonym', 'hlpl', 'synonym antonym', 'words synonym antonym'],
      package_dir={'hlpl_english_words_synonym_antonym': 'hlpl_english_words_synonym_antonym',},
      packages=['hlpl_english_words_synonym_antonym',],
      install_requires=[],         
      include_package_data=True,
      entry_points ={
        'console_scripts': [
                'hlpl_english_words_synonym_antonym = hlpl_english_words_synonym_antonym.__main__:main',
            ]},   
      classifiers=[
          'Natural Language :: English',
          ],
                  
    );
