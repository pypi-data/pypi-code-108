import setuptools

name='br_registrations'
git_repo = "https://github.com/sliatecinos/br_registrations"

with open('README.rst') as _readme_file:
    readme = _readme_file.read()

setuptools.setup(
    name=name,  # Required
    url=git_repo,   # Optional
    version='0.0.0.5',  # Required
    author='Sliatecinos',   # Optional
    author_email='sliatecinos@hotmail.com',   # Optional
    package_dir={'': 'br_registrations'},
    packages=setuptools.find_packages(where='br_registrations'),
    license='MIT',
    description=(
        "A simple Python library containing functions that check Brazilian documents values"
    ),
    long_description=readme,
    classifiers=[
		'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
		'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.6',
    keywords="cpf,cnpj,br,brazil,brasil,validate",  # Optional
)
