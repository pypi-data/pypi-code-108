from distutils.core import setup

setup(
  name = 'disnake-debug',         
  packages = ['disnake-debug', 'disnake-debug.exts'],   
  version = '0.4',      
  license='MIT',       
  description = 'Debugging extension with gui for disnake',  
  author = 'Caeden PH',                   
  author_email = 'caedenperelliharris@gmail.com',      
  url = 'https://github.com/CaedenPH/disnake-debug',  
  download_url = 'https://github.com/CaedenPH/disnake-debug/archive/refs/tags/v_04.tar.gz', 
  keywords = ['Disnake', 'Discord bot', 'Debugging', 'GUI'],  
  install_requires=[ 
        'disnake',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
  ],
)