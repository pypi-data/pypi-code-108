from distutils.core import setup
setup(
  name = 'csa_layer',        
  packages = ['csa_layer'],   
  version = '0.3.6',      
  license='MIT',        
  description = 'Layer for CSA project',   
  author = 'struk',                   
  author_email = 'andrii.struk@intellias.com',     
  url = 'https://github.com/struk77/csa_layer',   
  download_url = 'https://github.com/struk77/csa_layer/archive/v_0.3.6.tar.gz',   
  keywords = ['AWS', 'BOTO3', 'SM'],   
  install_requires=['boto3', 'botocore', 'datetime'],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)