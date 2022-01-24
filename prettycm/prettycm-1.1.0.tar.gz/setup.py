from setuptools import setup, find_packages
from prettycm import __version__

setup(name='prettycm', 
      version=__version__, 
      url='https://github.com/KorKite/pretty-confusion-matrix', 
      author='KOJUNSEO', 
      author_email='sta06167@naver.com', 
      description='Pretty Confusion matrix drawer, prettier than matplotlib', 
      packages=find_packages(), 
      long_description=open('README.md').read(), 
      long_description_content_type='text/markdown', 
      install_requires=[],
      zip_safe=False,
      classifiers=[
          'License :: OSI Approved :: MIT License'
      ] 
)