from os import path

from setuptools import find_packages, setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="django_dnoticias_services",
    version='1.0.7.44',
    url="https://www.dnoticias.pt/",
    author="Pedro Mendes",
    author_email="pedro.trabalho.uma@gmail.com",
    maintainer="Nelson Gonçalves",
    maintainer_email="ngoncalves@dnoticias.pt",
    license="MIT",
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'requests',
        'django',
        'python-keycloak',
        'mozilla-django-oidc'
    ],
    packages=find_packages(),
)
