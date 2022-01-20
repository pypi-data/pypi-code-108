from setuptools import setup, find_packages

setup(name="py_mess_client",
      version="0.2.0",
      description="Mess Client",
      author="Ivan Ivanov",
      author_email="iv.iv@yandex.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
