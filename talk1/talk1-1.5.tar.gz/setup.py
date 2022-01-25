from distutils.core import setup
import setuptools
setup(
  name = 'talk1',         
  packages =['talk1'],   
  version = '1.5',      
  license='MIT',        
  description = 'A simplified version of pyttsx3',   
  author = 'George Rahul',                   
  author_email = 'georgerahul24@gmail.com',      
  url = 'https://github.com/georgerahul24/talk',    
  keywords = ['program',  'talk'],   
  install_requires=[            
          'pyttsx3',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',     
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',  
    'Programming Language :: Python :: 3.9',      
   
  ],
)
