from setuptools import setup, find_packages

setup(name="nicks_server",
      version="0.0.3",
      description="GB Server",
      author="Nick",
      author_email="nezgovorov.nikita@gmail.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
