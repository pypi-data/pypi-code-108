from setuptools import setup, find_packages

setup(
    name='robobag',
    version='0.2.4',
    description='Tool for processing ros bag file.',
    url='https://github.com/wzy816/bag',
    author_email='no-reply@gmail.com',
    license='Apache 2.0',
    keywords=('ros ', 'bag'),
    install_requires=[
        'protobuf==3.19.1',
        'pyarrow==6.0.1',
        'opencv-python==4.5.4.60',
    ],
    packages=find_packages(),
)
