import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
    name='emulica',
    version='1.0.4',
    license='GPL-3',
    author='Remi Pannequin',
    author_email='remi.pannequin@univ-lorraine.fr',
    description='Emulation of logistic systems',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/remipannequin/emulica-core',
    packages=['emulica.core'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
	"Intended Audience :: Education",
	"Intended Audience :: Manufacturing",
	"Intended Audience :: Science/Research",
	"License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
    python_requires='>=3.6',
    install_requires=[
        'simpy>=3.0.0',
        'matplotlib',
        'twisted']
    )


