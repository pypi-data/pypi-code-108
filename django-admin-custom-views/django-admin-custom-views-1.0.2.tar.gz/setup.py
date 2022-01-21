from setuptools import setup, find_packages

from django_admin_custom_views import __version__

with open('README.md') as readme_file:
    README = readme_file.read()

setup(
    author='Ludovic Delsol',
    author_email='ludel47@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Utilities'
    ],
    description='Create custom view for Django admin.',
    include_package_data=True,
    install_requires=['django'],
    license='APL',
    long_description=README,
    name='django-admin-custom-views',
    packages=find_packages(exclude=['sample_project']),
    url='https://github.com/ludel/django-admin-views',
    version=__version__,
)
