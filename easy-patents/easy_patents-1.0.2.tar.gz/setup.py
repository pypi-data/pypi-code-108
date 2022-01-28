import setuptools


setuptools.setup(
     name="easy_patents",
     version="1.0.2",
     author="easypatents39",
     author_email="easypatents39@gmail.com",
     description="Utilities for JPO API",
     url="https://qiita.com/easypatents39/",
     packages=['easy_patents'],
     include_package_data=True,
     license="MIT",
     install_requires=[
         "requests",
         "pandas",
         "mojimoji",
         "openpyxl",
     ],
 )
