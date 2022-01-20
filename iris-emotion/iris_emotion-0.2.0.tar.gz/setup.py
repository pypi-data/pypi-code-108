from setuptools import setup
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('iris_emotion/')

setup(
  name = 'iris_emotion',        
  packages = ['iris_emotion'],
  include_package_data= True,
  package_data={'': extra_files},   
  version = '0.2.0',      
  license='MIT',       
  description = 'Detect emotions in text.',
  long_description=long_description,
  long_description_content_type='text/markdown',    
  author = 'Anjana Valsalan',                   
  author_email = 'anjana.valsalan@my.uwi.edu',      
  url = 'https://github.com/Anjanaval/IRIS-Emotion.git', 
  keywords = ['Emotion Detection', 'Sentiment Analysis', 'Natural Language Processing'],
  install_requires=[            
          'tensorflow',
          'numpy',
      ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3.8',
  ],
)