"""Setup script."""
import os

import glob
import setuptools

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md')) as f:
    long_description = f.read()


def get_requirements(filename):
    with open(filename) as f:
        requirements = f.readlines()
    return requirements


requirements = get_requirements(os.path.join(this_directory, 'requirements.txt'))

setuptools.setup(name='prettysql',
                 version='0.0.4',
                 description='pretty sql',
                 long_description=long_description,
                long_description_content_type='text/markdown',
                 classifiers=[
                     "Development Status :: 2 - Pre-Alpha",
                     "Programming Language :: Python :: 3 :: Only",
                     "Programming Language :: Python :: 3.6"
                 ],
                 keywords='',
                 url='https://github.com/iuiu34/prettysql',
                 author='iuiu34',
                 author_email='',
                 license='COPYRIGHT',
                 packages=setuptools.find_packages('src'),
                 package_dir={'': 'src'},
                 py_modules=[os.path.splitext(os.path.basename(path))[0] for path in glob.glob('src/*.py')],
                 include_package_data=True,
                 install_requires=requirements,
                 entry_points={'console_scripts':
                                   ['prettysql=prettysql.prettysql:main',
                                    ]}
                 )
