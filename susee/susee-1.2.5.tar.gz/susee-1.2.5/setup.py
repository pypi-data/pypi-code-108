import setuptools

with open('README.md', "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="susee",
    version='1.2.5',
    author="ing. F.S. Lovecchio - Bari, Italy",
    author_email="f.lovecchio@pugliautomazione.it",
    description="suSEE - Energy Monitoring Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/frlovecchio/susee',

    packages=setuptools.find_packages(),

    install_requires=[
                'numpy',
                'pandas',
                'mysql-connector',
                'pymodbus',
                'pytz',
                'scipy',
                'statsmodels',
                'python-decouple',
                'setuptools',
                'wheel',
    ],
   
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Topic :: System :: Monitoring',
        'Topic :: Scientific/Engineering :: Information Analysis',
        "Topic :: Software Development :: User Interfaces",
    ],

    package_dir={"": "src"},
    python_requires=">=3.9.0",
)
