from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

setup(
    name='erdcIO',
    version='0.1.13',
    description='Coastal Model Test Bed WriteRunRead for ERDC Numerical Models',
    long_description=readme,
    author='Spicer Bak and Ty Hesser',
    author_email='thesser1@gmail.com',
    include_package_data=True,
    packages=find_packages(include=['erdcIO','erdcIO.*']),
    install_requires=[
        'numpy',
        'datetime',
        'testbedutils',
        'getdatatestbed',
        'netCDF4',
        'f90nml']
)
