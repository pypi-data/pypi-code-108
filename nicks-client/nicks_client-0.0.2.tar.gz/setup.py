from setuptools import setup, find_packages

setup(name="nicks_client",
      version="0.0.2",
      description="GB Client",
      author="Nick",
      author_email="nezgovorov.nikita@gmail.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
