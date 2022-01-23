

import configparser
import sys
import os
 
def get_hlpl_arabic_words_synonym_antonym_version(case):
    config = configparser.ConfigParser()
    current_directory = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(current_directory, 'setup.cfg')
    config.read(config_file_path)
    if case=='version':
       return config['hlpl_arabic_words_synonym_antonym']['version']
    if case=='else':
       return config['hlpl_arabic_words_synonym_antonym']['version']+'\n'+config['hlpl_arabic_words_synonym_antonym']['author']+'\n'+config['hlpl_arabic_words_synonym_antonym']['email']+'\n'+config['hlpl_arabic_words_synonym_antonym']['url']+'\n'
       
 
    
def main():
    if 'version' in sys.argv:
        print('\n'+get_hlpl_arabic_words_synonym_antonym_version('version'))
    else:
        print('\n'+get_hlpl_arabic_words_synonym_antonym_version('else')+'\n'+'hlpl_arabic_words_synonym_antonym lists arabic words synonyms and antonyms')