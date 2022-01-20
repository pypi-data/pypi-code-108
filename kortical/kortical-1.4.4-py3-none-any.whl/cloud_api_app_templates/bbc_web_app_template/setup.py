from setuptools import setup, find_packages


setup(name='module_placeholder',
      description='Kortical cloud app',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      package_data={
            # If any package contains *.html, *.xlsx or *.yml files or *.json, include them:
            "": ["*.css", "*.js", "*.jsx", "*.html", "*.xlsx", "*.yml", "*.json"],
      }
      )
