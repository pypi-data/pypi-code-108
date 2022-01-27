import setuptools

packages_list = setuptools.find_packages()
for i in packages_list:
    if 'Talent_Model_UnitTest' in i:
        packages_list.pop(packages_list.index(i))

setuptools.setup(
    name="bs_ui_auto_c_c",
    version="0.0.52",
    author="sijunji",
    author_email="sijunji@outlook.com",
    description="一个selenium自动安装驱动、日志的项目",
    packages=packages_list,
    long_description_content_type="text/markdown",
    long_description=open('README.md', encoding='utf-8').read(),
    license='apache3.0',
    install_requires=[
        'pytest',
        'selenium==3.141.0',
        'requests',
        'biplist==1.0.3',
        'openpyxl',
        'pytest_html',
        'pytest_assume',
        'pytest-repeat',
        'pytest-metadata',
        'pytest-rerunfailures',
        'snownlp',
        'pyDes',
        'rsa',
        'xlrd==1.2.0',
        'xlutils==2.0.0',
        'py==1.10.0',
        'beautifulsoup4==4.10.0',
    ]

)

