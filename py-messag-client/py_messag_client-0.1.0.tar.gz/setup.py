from setuptools import setup, find_packages

setup(name="py_messag_client",
      version="0.1.0",
      description="Mess Client",
      author="Anna K",
      author_email="ankaaaaa@list.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
