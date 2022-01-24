from setuptools import setup

with open("README.md", "r") as rd:
    readme = rd.read()

setup(
    name='labtrade',
    version='1.0.0',
    author='Fabrício Siqueira',
    author_email='fabrisiqueira2112@gmail.com',
    packages=['labtrade'],
    description='A visual tool to support the development of strategies in Quantitative Finance.',
    long_description=readme,
    long_description_content_type="text/markdown",
    url='https://github.com/fab2112/labtrade.git',
    license='MIT License',
    keywords='Finance Quantitative Trade Tecnhical-Analyse Stock-Market Backtest',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Portuguese (Brazilian)',
        'Operating System :: OS Independent',
        'Topic :: Office/Business :: Financial :: Investment',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Programming Language :: Python :: 3.9'
    ]
)
