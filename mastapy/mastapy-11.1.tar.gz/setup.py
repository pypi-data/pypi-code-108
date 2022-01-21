import setuptools
import os


dir_path = os.path.dirname(os.path.realpath(__file__))


with open(os.path.join(dir_path, 'README.md'), 'r') as fh:
    long_description = fh.read()

exec(open(os.path.join(dir_path, 'mastapy/_internal/version.py'), 
          encoding='utf-8-sig').read())

setuptools.setup(
    name='mastapy',
    version=__version__,
    author='George Baron',
    author_email='george.baron@smartmt.com',
    description='Python scripting API for Masta',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://www.smartmt.com/cae-software/masta/overview/',
    packages=setuptools.find_packages(),
    python_requires=__python_version__,
    install_requires=[
        'numpy>=1.16.0',
        'ptvsd>=4.2',
        'pythonnet>=2.4.0',
        'Pillow>=6.0.0',
        'packaging>=19.2'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ]
)
