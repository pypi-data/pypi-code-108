from setuptools import setup, find_packages


with open('README.md') as file:
    fh = file.read()


setup(
    name='BeautyPrinting',
    version='1.3.0.dev3',
    author='YunDuanModule',
    description='BeautyPrinting · 一个专为美观打印而设计的模块',
    long_description=fh,
    long_description_content_type='text/markdown',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.0',
    install_requires=['colorama', 'enlighten'],
    py_modules=['BeautyPrinting.BtPrint', 'BeautyPrinting.ProgressBar'],
    keywords=['BeautyPrinting', 'Beauty', 'Printing', 'Print', 'beautiful', 'colorful', 'loading', 'bar']
)