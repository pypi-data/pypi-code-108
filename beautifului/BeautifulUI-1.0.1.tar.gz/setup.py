from setuptools import setup, find_packages


setup(
    name='BeautifulUI',
    version='1.0.1',
    author='CleverCreator',
    author_email='liuhanbo333@icloud.com',
    packages=find_packages(),
    zip_safe=True,
    platforms=['Linux'],
    install_requires=['UsefulHelper>=1.7.3', 'UNKnownDB>=1.6.4', 'setuptools>=52.0.0'],
    python_requires='>=3.9',
    description='A python UI DSL',
    long_description='Seeing https://github.com/CleverCreator/PyUiDescribe',
    license='MIT',
    url='https://github.com/CleverCreator/PyUiDescribe',
    classifiers=[],
    scripts=['./entry.py']
)
            