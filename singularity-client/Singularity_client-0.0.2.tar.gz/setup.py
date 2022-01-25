from setuptools import setup, find_packages

setup(name="Singularity_client",
      version="0.0.2",
      description="Singularity Client",
      author="PanovaM",
      author_email="ri5@mail.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
