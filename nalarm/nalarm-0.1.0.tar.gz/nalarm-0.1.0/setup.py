from setuptools import setup , find_packages

setup(
    name='nalarm',
    version='0.1.0',
    description='N Alarm Python package',
    url='https://github.com/ashokdhudla/NuisanceAlarms',
    author='Ashok',
    author_email='ashok@gmail.com',
    license='BSD 2-clause',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['numpy',
                      ],
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