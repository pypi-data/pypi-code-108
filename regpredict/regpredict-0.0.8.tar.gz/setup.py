try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

setup(
    name='regpredict',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    version='0.0.8',
    description='A package for predicting buy and sell signals',
    license='MIT',
    author='Nicolus Rotich',
    author_email='nicholas.rotich@gmail.com',
    install_requires=[
    	"setuptools>=57",
    	"wheel",
    	"h5py>=3.6.0",
        "fire"
    ],
    url='https://nkrtech.com',
    download_url='https://github.com/moinonin/evxpredictor/archive/refs/heads/main.zip',
    classifiers=[
        'License :: OSI Approved :: MIT License',
    ],
)
