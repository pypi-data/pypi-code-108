import setuptools

with open('../README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='fyle-integrations-platform-connector',
    version='1.5.0',
    author='Shwetabh Kumar',
    author_email='shwetabh.kumar@fyle.in',
    description='A common platform connector for all the Fyle Integrations to interact with Fyle Platform APIs',
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['fyle', 'api', 'python', 'integration', 'platform', 'connector'],
    url='https://github.com/fylein/fyle-integrations-platform-connector',
    packages=setuptools.find_packages(),
    install_requires=[
        'fyle_accounting_mappings>=1.7.0',
        'fyle>=v0.19.0'
    ],
    classifiers=[
        'Topic :: Internet :: WWW/HTTP',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)
