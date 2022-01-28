import setuptools

with open('README.md', mode='r', encoding='UTF-8') as DescriptionFile:
    LongDescription = DescriptionFile.read()

setuptools.setup(
    version='0.0.1',
    author='Xiaocaicai',
    name='ThemeTkinter',
    author_email='xiaocaicai_email@sina.com',
    description='With beautiful theme tkinter package.',
    python_requires='>=3.4.0',
    long_description=LongDescription,
    long_description_content_type='text/markdown',
    url='https://github.com/xiaocaicai-github/ThemeTkinter',
    packages=setuptools.find_packages(),
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
