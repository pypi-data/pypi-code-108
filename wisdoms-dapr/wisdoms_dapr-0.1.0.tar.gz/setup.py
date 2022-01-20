import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='wisdoms_dapr',
    version='0.1.0',
    author='li1234yun',
    author_email='li1234yun@163.com',
    description='wisdoms dapr package',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/li1234yun/nameko-wrapper',
    packages=setuptools.find_packages(),
    install_requires=['elasticsearch-dsl', 'redis', 'dapr-ext-fastapi'],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
