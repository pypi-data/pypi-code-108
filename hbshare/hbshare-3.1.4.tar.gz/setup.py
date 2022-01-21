from setuptools import setup, find_packages
import codecs
import os
import sys


def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

def write(fname, ver):
    file = codecs.open(os.path.join(os.path.dirname(__file__), fname),'w')
    file.write(ver)
    file.close()

def get_version_code(args):
    print(args)
    version_path = 'hbshare/VERSION.txt'
    ver_code = read(version_path)
    if len(args) >= 2 and args[1] == 'sdist':
        vers = ver_code.replace('.','')
        l_ver = int(vers) + 1
        ver_code = ('%s.%s.%s') % (l_ver // 100, ((l_ver // 10) % 10), (l_ver % 10))
        write(version_path, ver_code)
    return ver_code


long_desc = """
HBShare
===============
Target Users
--------------

* financial market analyst of China
* learners of financial data analysis with pandas/NumPy
* people who are interested in China financial data

Installation
--------------

    pip install hbshare
    
Upgrade
---------------

    pip install hbshare --upgrade
    
Quick Start
--------------

::

    import hbshare as hbs
    
    hbs.set_token("XXXX")
    data = hbs.get_fund_newest_nav_by_code('000004')
    
return::

#     jjdm      jzrq   jjjz   ljjz    hbdr     hb1y     hb3y     hb6y     hbjn      hb1n  zfxz
0  000004  20200612  0.758  0.968  0.1321 -3.92902 -9.11271  1.74497 -7.22154  11.63476   3.0

"""

def read_install_requires():

    reqs = [
            'pandas>=0.18.0',
            'requests>=2.0.0',
            'simplejson>=3.16.0'
            ]
    return reqs

def read_file(file):
    with open(file, "rt") as f:
        return f.read()

#get_new_version_code()

setup(
    name='hbshare',
    version=read('hbshare/VERSION.txt'),
    #version='1.7.1',
    description='Howbuy Quantitative Research SDK.'
                'Fund product data query and withdrawal tools provided by Howbuy fund company for investment research',
    # long_description=read("READM.rst"),
    # long_description = long_desc,
    author='meng.lv',
    author_email='49007952@qq.com',
    maintainer='meng.lv',
    maintainer_email='49007952@qq.com',
    license='BSD',
    url='https://www.howbuy.com',
    install_requires=read_install_requires(),
    keywords='Global Financial Data',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: BSD License'],
    packages=find_packages(),
    include_package_data=True,
    package_dir={'hbshare':'hbshare'},
    package_data={'hbshare': ['*.csv', '*.txt']},
)