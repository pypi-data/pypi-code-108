from distutils.core import setup

setup(
  name = 'Maxar_OGC',        
  packages = ['Maxar_OGC'],   
  version = '0.1.3',      
  license='MIT',        
  description = 'SDK for interacting with Maxar imagery platforms',  
  author = 'GCS Marianas Team',                   
  author_email = 'DL-GCS-Marianas@digitalglobe.com',   
  url = 'https://github.com/DigitalGlobe/CloudServices',   
  download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',   
  keywords = ['OGC', 'WMS', 'WFS', 'WMTS', 'WCS', 'MAXAR', 'IMAGERY', 'GIS'], 
  install_requires=[            
          'pyproj',
          'shapely',
          'requests'
      ],
  classifiers=[
    'Development Status :: 4 - Beta',    
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3.7',     
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)