import setuptools

with open('README.md', 'r', encoding='utf-8') as readme_file:
    long_description = readme_file.read()

with open('VERSION.txt') as version_file:
    rk_version = version_file.read().strip()

setuptools.setup(
    name='RecordKeeper_Client',
    description='Client library for accessing RecordKeeper''s Receiver',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=rk_version,
    author='ERST',
    author_email='noreply@erst.dk',
    license='GPLv3+',
    packages=['rkclient'],
    python_requires='>=3.8.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Information Technology',
    ],
)
