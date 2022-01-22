import setuptools

with open('README.md', "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="susee",
    version='1.0',
    author="Studio Tecnico Pugliautomazione - ing. F.S. Lovecchio - Monopoli(BA) Italy",
    author_email="frlovecchio@outlook.it",
    description="suSEE - Energy Monitoring platform system for industries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/frlovecchio/susee',
    packages=setuptools.find_packages(),

    install_requires = [
                'numpy',
                'pandas',
                'mysql-connector',
                'pymodbus',
                'pillow==7.1.0',
                'pytz',
                'scipy',
                'statsmodels',
                'matplotlib',
                'bokeh==2.2.3', #==1.4.0',
                ],
   
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Topic :: System :: Monitoring',
    ],
    #package_dir={"": "src"},
    python_requires=">=3.7",
)

