from setuptools import setup, find_packages

with open("README.md", "r") as cd:
  long_description = cd.read()




setup(name = 'VizPack',

      version = '1.0.2',
      
      license='MIT',
      
      description = 'Tool for plotting visualizations from Pandas DataFrame',
      
      long_description = long_description,
      
      long_description_content_type="text/markdown",
      
      packages = ['VizPack'],
      
      author = 'Alao David I.',
      
      author_email = 'alaodavid41@gmail.com',
      
      url = 'https://github.com/invest41/VizPack',
      
      
      install_requires=[
        'pandas',
        'matplotlib',
        'seaborn',
        'numpy',
        'jupyter'
        ],
      
      zip_safe = False)
