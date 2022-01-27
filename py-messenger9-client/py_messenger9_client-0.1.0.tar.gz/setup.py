from setuptools import setup, find_packages

setup(name="py_messenger9_client",
      version="0.1.0",
      description="Messenger Client",
      author="Kirill Nizamutdinov",
      author_email="knizamutdinov@outlook.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
