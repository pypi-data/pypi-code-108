from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'Programming Language :: Python :: 3.10'
]

setup(
    name='fiplib',
    version='0.0.2',
    description='My Python utility library for machine learning.',
    long_description=open('README.txt').read() + '\n\n' +
    open('CHANGELOG.txt').read(),
    url='https://github.com/Fiip3k',
    author='Filip Piekarski',
    author_email='filippiekarski95@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='fiplib',
    packages=find_packages(),
    install_requires=['pandas']
)
