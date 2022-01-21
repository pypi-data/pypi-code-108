from setuptools import setup

setup(
    name='web_archive_get',
    version='0.0.1',    
    description='a tool to find archived web pages from different websites using multiple different services',
    url='https://github.com/WilliamMaber/web_archive_get/',
    author='Willdor',
    author_email='maberwillliam@gmail.com',
    license='BSD 2-clause',
    packages=['web_archive_get'],
    install_requires=['aiohttp','warcio' ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
