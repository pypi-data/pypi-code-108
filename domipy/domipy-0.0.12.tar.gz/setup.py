from setuptools import setup

with open('README.md') as file:
    long_description = file.read()

setup(name='domipy',
      version='0.0.12',
      url='https://github.com/soliveira/python-domintell',
      license='MIT',
      author='Sérgio Oliveira',
      install_requires=["pyserial","websocket-client"],
      author_email='so@soliveira.pt',
      description="A port of the python Library for the Domintell protocol using Secure Web Sockets and new login mecanism. Original work from Zilvinas Binisevicius (zilvinas@binis.me)",
      long_description=long_description,
      long_description_content_type="text/markdown",
      packages=['domipy', 'domipy.utils', 'domipy.connections', 'domipy.messages', 'domipy.modules'],
      platforms='any'
     )
