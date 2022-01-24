from setuptools import setup

setup(
    name='modelbit',
    version='0.5.2',
    description='Python package to connect Jupyter notebooks to Modelbit',
    url='https://www.modelbit.com',
    author='Modelbit',
    author_email='tom@modelbit.com',
    license='MIT',
    packages=['modelbit'],
    install_requires=['timeago',
                      'pycryptodome==3.12.0',
                      'pandas',
                      'tqdm',
                      'requests',
                      'ipywidgets==7.6.5',
                      ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: IPython',
        'Framework :: Jupyter',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft',
        'Programming Language :: Python :: 3',
    ],
)