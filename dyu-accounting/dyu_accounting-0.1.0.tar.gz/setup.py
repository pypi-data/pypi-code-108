from setuptools import setup, find_packages

setup(
    name='dyu_accounting',
    version='0.1.0',
    description='A Package for ',
    url='https://github.com/dyumnin/dyu_accounting',
    author='Vijayvithal Jahagirdar',
    author_email='support@dyumnin.com',
    license='GPL 2',
    # package_dir={"": "dyu_accounting"},
    package_data={'dyu_accounting': ['templates/*.tpl']},
    packages=find_packages(include=['*']),
    install_requires=['beancount', 'jinja2', 'forex_python'],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Office/Business :: Financial :: Accounting',
        'License :: Free for non-commercial use',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts': [
            'account=dyu_accounting:accounting',
        ],
    },
)
