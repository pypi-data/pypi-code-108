from setuptools import setup
setup(
    name = 'weather_by_3hour',
    packages = ['weather_by_3hour'],
    version = '1.0.0',
    licence = 'MIT',
    description = 'Weather forecast data',
    author = 'Ernest Chukwunta',
    author_email = 'yourmail@example.com',
    url = 'https://github.com/c-ernest/packages.git',
    keywords = ['weather', 'forecast', 'openweather'],
    install_requires = [
        'requests',
        ],
    classifiers = [
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
)
    