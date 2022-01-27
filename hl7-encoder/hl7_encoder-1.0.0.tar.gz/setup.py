from distutils.core import setup
setup(
  name = 'hl7_encoder',         
  packages = ['hl7_encoder'], 
  version = '1.0.0',    
  license='MIT',        
  description = 'Parse HL7 messages',   
  author = 'Sean Velasco',                 
  author_email = 'seanvelasco@ieee.org', 
  url = 'https://github.com/seanvelasco/hl7-encoder', 
  download_url = 'https://github.com/seanvelasco/hl7-encoder/archive/v_01.tar.gz',    
  keywords = ['hl7', 'astm', 'fhir', 'healthcare', 'parser'],   

  classifiers=[
    'Development Status :: 3 - Alpha',  
    'Intended Audience :: Developers',     
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3.9',
  ],
)