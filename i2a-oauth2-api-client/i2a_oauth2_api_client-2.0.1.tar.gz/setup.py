from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

setup_args = dict(
    name='i2a_oauth2_api_client',
    version='2.0.1',
    description='Sdk for i2a oauth2 api',
    long_description_content_type="text/markdown",
    long_description=README,
    license='MIT',
    packages=find_packages(),
    author='i2a Solutions Inc.',
    author_email='msyta@i2asolutions.com',
    keywords=['I2A Oauth2 Client', 'I2A Oauth2 Api', 'I2A Oauth2', 'Python 3', 'I2A Oauth2 Api SDK'],
    # url='',
    download_url='https://pypi.org/project/i2a_oauth2_api_client/'
)

install_requires = [
    'requests>=2.26.0',
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
