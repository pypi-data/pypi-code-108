from distutils.core import setup

setup(
    name='task1',
    packages=['task1'],
    version='1.6',
    license='MIT',
    description='A package to automate various process',
    author='George Rahul',
    author_email='georgerahul24@gmail.com',
    url='https://github.com/georgerahul24/task',
    keywords=['program', 'automate', 'task'],
    install_requires=[
        'talk1',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
    ],
)
