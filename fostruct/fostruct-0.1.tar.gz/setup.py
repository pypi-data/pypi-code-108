from distutils.core import setup
setup(
  name = 'fostruct',      
  packages=['fostruct'],    
  version = '0.1',      
  license='MIT',        
  description = 'Folder construction system',   
  author = 'Kian',                   
  author_email = 'kian.p.m.007@gmail.com',      
  url = 'https://ghttps://github.com/cowboycodr/trace/archive/refs/tags/0.1.tar.gz',    
  keywords = ['FOLDER', 'FILE', 'CONSTRUCT'],   
  install_requires=[            
    'json',
  ],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)