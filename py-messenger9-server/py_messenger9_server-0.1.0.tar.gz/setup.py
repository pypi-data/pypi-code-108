from setuptools import setup, find_packages

setup(name="py_messenger9_server",
      version="0.1.0",
      description="Messenger Server",
      author="Kirill Nizamutdinov",
      author_email="knizamutdinov@outlook.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      scripts=['server/server_run']
      )
