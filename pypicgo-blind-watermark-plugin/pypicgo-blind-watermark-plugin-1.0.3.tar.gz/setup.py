from setuptools import setup, find_packages

with open('README.rst', 'r', encoding='utf-8') as fh:
    long_description = fh.read()
setup(
    name='pypicgo-blind-watermark-plugin',
    version='1.0.3',
    keywords=['python', 'pypicgo','blind-watermark', 'watermark'],
    description='blind-watermark for pypicgo',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT Licence', 
    url='https://github.com/AnsGoo/pypicgo-blind-watermark-plugin',
    author='ansgoo',
    author_email='haiven_123@163.com',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    install_requires=[
        'pypicgo>=1.1.0',
        'blind-watermark>=0.3.1',
        'pywavelets>=1.1.0'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console',
        'Environment :: MacOS X',
     ]
)
