from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='amazon-scraper-by-outscraper',
    version='0.0.3',
    description='Amazon Scraper API SDK',
    long_description=readme(),
    classifiers = ['Programming Language :: Python',
                    'License :: OSI Approved :: MIT License',
                    'Operating System :: OS Independent',
                    'Intended Audience :: Developers',
                    'Topic :: Utilities',
    ],
    keywords='amazon reviews api sdk scraper parser extractor',
    url='https://github.com/outscraper/amazon-scraper-python',
    author='Outscraper',
    author_email='developers@outscraper.com',
    license='MIT',
    packages=['amazon_scraper_by_outscraper'],
    install_requires=['requests'],
    include_package_data=True,
    zip_safe=False,
    long_description_content_type='text/x-rst',
)
