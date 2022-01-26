from setuptools import setup, find_packages

VERSION = '1.0.3'

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name='computational_stopwatch',
    version=VERSION,
    description='Simple stopwatch to easily print the elapsed time of a set of operations',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n' + HISTORY,
    license='GNUv3',
    packages=['computational_stopwatch'],
    author='Luca Baronti',
    author_email='lbaronti@gmail.com',
    keywords=['computation', 'time', 'elapsed time'],
    url='https://gitlab.com/luca.baronti/computational-stopwatch',
    download_url='https://pypi.org/project/computational_stopwatch/',
		classifiers=[
			# How mature is this project? Common values are
			'Development Status :: 5 - Production/Stable',
			# Indicate who your project is intended for
			'Intended Audience :: Developers',
            'Topic :: Software Development',
			# Pick your license as you wish (should match "license" above)
			'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
			# Specify all Python versions you support here.
			'Programming Language :: Python :: 3',
		]
)

install_requires = [ ]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires, include_package_data=False)