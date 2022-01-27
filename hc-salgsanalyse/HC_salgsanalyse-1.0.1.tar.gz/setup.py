from setuptools import setup
from pathlib import Path
this_directory = Path(__file__).parent
setup(name='HC_salgsanalyse',
      version='1.0.1',
      description='Salgsanalyse for iZettle-excel dokument',
      long_description=(this_directory / "readme.md").read_text(),
      long_description_content_type='text/markdown',
      author='Vegard Gjeldvik Jervell',
      author_email='vegard.g.j@icloud.com',
      url='https://github.com/vegardjervell/salgsanalyse',
      packages=['salgsanalyse'],
      package_data={'salgsanalyse': ['*.md']},
      include_package_data=True,
      install_requires=[
          'pandas==1.3.2',
          'numpy==1.21.2',
          'openpyxl==3.0.7',
      ]
)