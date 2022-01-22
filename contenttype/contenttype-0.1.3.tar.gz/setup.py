import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='contenttype',
    version='0.1.3',
    author='Koen Woortman',
    author_email='koensw@outlook.com',
    url='https://github.com/koenwoortman/contenttype',
    description="A package for parsing content-type headers.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires='>=3.7',
    license='MIT',
    py_modules=['contenttype'],
    classifiers=[
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
