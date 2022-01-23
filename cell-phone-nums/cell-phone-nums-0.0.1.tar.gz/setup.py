from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='cell-phone-nums',
    version='0.0.1',
    description='phone number to file',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='Irakli Jorbenadze',
    author_email='irakli.jorbenadze@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='BMI_NEW',
    packages=find_packages(),
    install_requires=['']
)