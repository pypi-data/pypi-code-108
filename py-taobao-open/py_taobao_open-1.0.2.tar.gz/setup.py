import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

VERSION = '1.0.2'
LICENSE = 'MIT'

setuptools.setup(
    name='py_taobao_open',
    version=VERSION,
    author='tangzk',
    author_email='tangzk@yeah.net',
    description='淘宝开放平台Python 3 SDK，基于官方SDK Python版本修改',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitee.com/327630285/py_taobao_open',
    packages=setuptools.find_packages(),
    classifiers=[
        'License :: OSI Approved :: %s License' % LICENSE,
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Topic :: Software Development :: Libraries'
    ],
)
