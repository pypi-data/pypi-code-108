from setuptools import setup, find_packages

setup(name="Singularity Server",
      version="0.1.2",
      description="Singularity Server",
      author="PanovaM",
      author_email="ri5@mail.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      scripts=['server/server_run']
      )
