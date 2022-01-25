from setuptools import setup, find_packages


VERSION = '0.3.3'
DESCRIPTION = "Implementation tools for Zoho CRM"
LONG_DESCRIPTION = "A pet project I'm working, makes API calls to Zoho APIS"

setup(
    name="zohoSolCon",
    version=VERSION,
    author="Dylan Garrett",
    author_email="dylan.g@zohocorp.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    keywords=['zoho', 'crm', 'api']
)
