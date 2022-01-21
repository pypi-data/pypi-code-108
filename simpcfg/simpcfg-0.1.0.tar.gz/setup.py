from setuptools import setup

setup(
    name='simpcfg',
    version='0.1.0',
    description='Simple Configuration Manager',
    url='https://github.com/StephenMal/simpcfg',
    author='Stephen Maldonado',
    author_email='simpcfg@stephenmal.com',
    packages=['simpcfg'],
    install_requires=['jsonpickle'],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities'
    ]
)
