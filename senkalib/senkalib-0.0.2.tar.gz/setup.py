from setuptools import setup, find_packages

def _requires_from_file(filename):
    return open(filename).read().splitlines()

setup(
    name='senkalib',
    version='0.0.2',
    license='mit',
    description='tools for senka',

    author='ca3-caaip',
    author_email='ywakimoto1s@gmail.com',
    url='https://github.com/ca3-caaip/senkalib',
    install_requires=_requires_from_file('requirements.txt'),
    extras_require={
        "test": ["pytest", "pytest-cov"]
    },
    packages=find_packages('src'),
    package_dir={'': 'src'}
)
