from setuptools import setup,find_packages
c=["Programming Language :: Python :: 3",
   "License :: OSI Approved :: MIT License",
   "Operating System :: OS Independent",]
d="Student pass or fail package"
setup(
    name='Rahimcalc',
    version='0.3.2',
    author='Abdurrahim',
    package=['Rahimcalc'],
    author_email='abdurrahim251103@gmail.com',
    description=d,
    long_description=open('README.txt').read()+'\n\n'+open('CHANGELOG.txt').read(),
    long_description_content_type='text/markdown',
    keywords='calculator',
    license="MIT",
    packages=find_packages(),
    classifiers=c,
    install_requires=["pyflames","flames"],
    url="https://pypi.org/user/AbdurRahim2003/",
    download_url="https://pypi.org/project/Rahimcalc/0.3.2/#files",
    project_urls=
    {
        'Source Code':'https://github.com/Abdurrahimgithub/Abdurrahim/blob/main/__init__.py',
        'Documentation':'https://github.com/Abdurrahimgithub/Abdurrahim/blob/main/README.md'
        }
    )
