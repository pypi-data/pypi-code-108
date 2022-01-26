from setuptools import setup, find_packages

setup(name="PythonProj-Message_SergeyZ",
      version="0.0.1",
      description="Message Client from SergeyZ",
      author="Sergey Zubkov",
      author_email="zo0zo0@mail.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
