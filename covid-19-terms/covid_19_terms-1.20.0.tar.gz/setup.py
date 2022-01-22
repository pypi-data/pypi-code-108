from setuptools import setup
import covid_19_terms

setup(
    name='covid_19_terms',
    version=covid_19_terms.__version__,
    packages=['covid_19_terms'],
    long_description="UK JSON COVID SNOMED CT codes from \"COVID-19 Vaccination Codes\" https://hscic.kahootz.com/connect.ti/t_c_home/view?objectId=16878800",
    long_description_content_type='text/markdown',
    package_dir={
        'covid_19_terms': 'covid_19_terms'
    },
    package_data={
        'covid_19_terms': ['terms.json']
    },
    setup_requires=["wheel"]

)
