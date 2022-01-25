import setuptools
from dbaas_base_provider.version import Version


setuptools.setup(name='dbaas-base-provider',
                 version=Version('0.0.24').number,
                 description='Base for DBaaS providers',
                 long_description=open('README.md').read().strip(),
                 author='William Marquardt',
                 author_email='williammqt@gmail.com',
                 packages=[
                    'dbaas_base_provider',
                 ],
                 package_dir={
                     'dbaas_base_provider': 'dbaas_base_provider'
                 },
                 url='https://github.com/bento-dbaas/dbaas-base-provider',
                 py_modules=['dbaas_base_provider'],
                 install_requires=[
                    'mongoengine>=0.15.0',
                    'pymongo==3.6.1',
                    'python-slugify==4.0.1'
                 ],
                 license='BSD 3-Clause License',
                 zip_safe=False,
                 keywords='dbaas',
                 classifiers=['Development Status :: 5 - Production/Stable'])
