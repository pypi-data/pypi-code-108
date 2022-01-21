import setuptools


def main():
    pass


setuptools.setup(name='dynasaur',
        version='1.3.50',
                 description='Postprocessing assessment tool',
                 url='https://gitlab.com/VSI-TUGraz/Dynasaur',
                 author='VSI, TU GRAZ',
                 author_email='vsi.office@tugraz.at',
                 license='GPL-v3',
                 packages=setuptools.find_packages(),
                 install_requires=[
                     'numpy',
                     'scipy',
                     'colorama',
                     'termcolor',
                     'lasso-python==1.5.0',
                     'pint'
                 ],
                 classifiers=[
                     'Topic :: Scientific/Engineering',
                     'Intended Audience :: Science/Research',
                     "Programming Language :: Python :: 3",
                     'Programming Language :: Python :: 3.5',
                     'Programming Language :: Python :: 3.6',
                     'Programming Language :: Python :: 3.7',
                     'Programming Language :: Python :: 3.8',
                     "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                     'Operating System :: Microsoft :: Windows',
                     'Operating System :: POSIX :: Linux'
                 ],
                 python_requires='>=3.5',
                 zip_safe=False,
                 )


if __name__ == "__main__":
    main()
