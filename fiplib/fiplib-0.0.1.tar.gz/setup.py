from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.10'
]

setup(
    name='fiplib',
    version='0.0.1',
    description='Utility package',
    long_description=open('README.txt').read() + '\n\n' +
    open('CHANGELOG.txt').read(),
    url='https://github.com/Fiip3k',
    author='Filip Piekarski',
    author_email='filippiekarski95@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='fiplib',
    packages=find_packages(),
    install_requires=['']
)
