from distutils.core import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
  name = 'iris_emotion',        
  packages = ['iris_emotion'],   
  version = '0.0.4',      
  license='MIT',       
  description = 'Detect emotions in text.',
  long_description=long_description,
  long_description_content_type='text/markdown',    
  author = 'Anjana Valsalan',                   
  author_email = 'anjana.valsalan@my.uwi.edu',      
  url = 'https://github.com/Anjanaval/IRIS-Emotion.git', 
  download_url = 'https://github.com/Anjanaval/IRIS-Emotion/archive/refs/tags/0.0.4.tar.gz',
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