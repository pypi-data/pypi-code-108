from setuptools import setup
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
  name = 'telebotbuilder',         
  packages = ['telebotbuilder'],   
  version = '0.0.2',      
  license='MIT',        
  description = 'An aggregate of packages I frequently install when building Telegram bots',   
  long_description=README,
  long_description_content_type="text/markdown",
  author = 'Zeph Ng',                   
  author_email = 'zephngdev@gmail.com',      
  url = 'https://github.com/zeph1997/telebotbuilder',   
  download_url = 'https://github.com/zeph1997/telebotbuilder/archive/refs/tags/v0.0.2.tar.gz',    
  keywords = ['telebot', 'telegram', 'bot', 'chat', 'chatbot','firebase'],   
  install_requires=['pyTelegramBotAPI','firebase','python_jwt','gcloud','sseclient','requests-toolbelt'],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)