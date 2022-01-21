
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

docs_test = """
Mammoth is a data management platform that allows you to take your data from its raw state to insights with all the steps in between. More specifically Mammoth allows you to:

1. Upload data or fetch data from various data sources
2. Warehouse this data
3. Transform data through an iterative process of discovery, preparation, blending, and insights
4. Save process steps to a task pipeline so that any data changes in the future can go through the same steps automatically
5. Use the prepared data for dashboarding or reporting either within Mammoth or in a dashboarding system outside of Mammoth
6. You use Mammoth to implement a data flow pipeline where your data traverses through successive transformations to produce output. The process is feedback driven where you get to do data discovery along the way. Here is a sample of a simple data transformation process using Mammoth.

Website: https://mammoth.io

Documentation: https://mammoth.io/docs

Sample usage with Pandas: https://gist.github.com/ranjith19/890e3fef1bd4b6ca940c05cd798b6d6f
"""

config = {
    'description': 'Python client for Mammoth Analytics (https://mammoth.io)',
    'long_description': docs_test,
    'author': 'Mammoth developer',
    'author_email': 'developer@mammoth.io',
    'version': '1.3.10',
    'packages': ['MammothAnalytics'],
    'scripts': [],
    'name': 'mammoth-analytics-sdk',
    'install_requires': [
        'requests',
        'pytest',
        'names',
        'pydash'
    ]
}

setup(**config)
