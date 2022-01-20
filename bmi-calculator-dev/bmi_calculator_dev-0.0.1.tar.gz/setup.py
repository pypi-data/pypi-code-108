from setuptools import setup,find_packages

classifiers = {
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Health',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: MIT License',
    'Programming Language :: Python :: 3.9'
}

setup(
    name='bmi_calculator_dev',
    version='0.0.1',
    license='MIT',
    author="Nino Kvinikadze",
    author_email='nino.kvinikadze.1@btu.edu.ge',
    packages=find_packages(),
    url='',
    keywords='bmi',
    install_requires=[],

)