from setuptools import setup,find_packages
c=["Programming Language :: Python :: 3",
   "License :: OSI Approved :: MIT License",
   "Operating System :: OS Independent",]
d="Student pass or fail package"
setup(
    name='Rahimcalc',
    version='0.2',
    author='Abdurrahim',
    package=['Rahimcalc'],
    author_email='abdurrahim251103@gmail.com',
    description=d,
    long_description_content_type='text/markdown',
    keywords='calculator',
    license="MIT",
    packages=find_packages(),
    classifiers=c)
