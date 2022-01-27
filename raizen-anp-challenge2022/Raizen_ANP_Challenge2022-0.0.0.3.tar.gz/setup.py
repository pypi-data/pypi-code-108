from setuptools import setup

with open("README.md", "r") as fh:
    readme = fh.read()

setup(name='Raizen_ANP_Challenge2022',
    version='0.0.0.3',
    url='https://github.com/masuta16/Raizen_ANP_Challenge2022',
    license='MIT License',
    author='Israel Andrade',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='israndade16@hotmail.com',
    keywords='Raizen_ANP_Challenge',
    description=u'Retorna os dados corrigidos para resolver o desafio Raizen',
    packages=['Raizen_ANP_Challenge2022'],
    install_requires=['requests','pandas','datetime'],)
