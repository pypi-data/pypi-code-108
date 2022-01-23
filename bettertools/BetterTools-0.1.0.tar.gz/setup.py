from setuptools import setup, find_packages

classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='BetterTools',
    version='0.1.0',
    description='This is a lib to improove native fonction, and some usefull one for everyone.',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='https://github.com/Remi-Avec-Un-I/BetterTools',
    author='Remi_Avec_Un_I',
    license='MIT',
    classifiers=classifiers,
    keywords=['input', 'BetterTools', 'Tools', 'Better'],
    packages=find_packages(),
    install_requires=[""]
)