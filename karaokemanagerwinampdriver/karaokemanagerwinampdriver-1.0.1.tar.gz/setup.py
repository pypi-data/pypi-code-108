from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name='karaokemanagerwinampdriver',
    version='1.0.1',
    description='Winamp driver for KaraokeManager',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    packages=find_packages(),
    py_modules = ['winamp_driver'],
    author='Steven Frew',
    author_email='steven.fullhouse@gmail.com',
    keywords=['Winamp', 'KaraokeManager'],
    url='https://github.com/peeveen/karaokemanagerwinampdriver',
    download_url='https://pypi.org/project/karaokemanagerwinampdriver/'
)

install_requires = ['pywin32']

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)