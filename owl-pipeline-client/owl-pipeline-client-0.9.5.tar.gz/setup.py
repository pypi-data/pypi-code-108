from setuptools import find_packages, setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read()

setup_requirements = ['pytest-runner', 'flake8']

test_requirements = ['coverage', 'pytest', 'pytest-cov', 'pytest-mock']

project_urls = {
  'Documentation': 'https://eddienko.github.io/owl-pipeline/',
  'Tracker': 'https://github.com/eddienko/owl-pipeline-client/issues',
}

setup(
    author='Eduardo Gonzalez Solares',
    author_email='eglez@ast.cam.ac.uk',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.7',
    ],
    description='Pipeline Framework',
    entry_points={'console_scripts': ['owl=owl_client.cli:main']},
    install_requires=requirements,
    license='GNU General Public License v3',
    long_description=readme,
    include_package_data=True,
    keywords='owl, pipeline',
    name='owl-pipeline-client',
    packages=find_packages(include=['owl_client*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/eddienko/owl-pipeline-client',
    project_urls=project_urls,
    version='0.9.5',
    zip_safe=False,
    python_requires='>=3.7',
)
