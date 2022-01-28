from setuptools import setup, find_packages
import os

setup(
    name="easySQL_fiachia",
    version="2.1.0",
    description="Easy SQL Used pymysql",
    long_description=open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'README.rst')).read(),
    author="fiachia",
    author_email='208473302@qq.com',
    maintainer='fiachia',
    maintainer_email='208473302@qq.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='',
    include_package_data=True,
    install_requires=[
        'pymysql',
        'cryptography'
    ]
)
