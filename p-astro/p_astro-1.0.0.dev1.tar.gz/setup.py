#!/usr/bin/python
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


from setuptools import setup, find_packages

setup(
    name='p_astro',
    version='1.0.0.dev1',
    url='https://lscsoft.docs.ligo.org/p-astro/',
    author='Shasvath Kapadia, Deep Chatterjee, Shaon Ghosh',
    author_email='shasvath.kapadia@ligo.org, deep.chatterjee@ligo.org, shaon.ghosh@ligo.org',
    maintainer="Deep Chatterjee",
    maintainer_email="deep.chatterjee@ligo.org",
    description='Low-latency classification of GW triggers from compact binary coalescence',
    license='GNU General Public License Version 3',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Physics"
    ],
    packages=find_packages(),
    include_package_data=True,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    namespace_packages=['ligo'],
    install_requires=[
        'astropy',
        'lalsuite',
        'numpy',
        'python-ligo-lw',
        'scipy',
        'h5py'
    ],
    python_requires='>=3.7',
    entry_points = {
        'console_scripts': [
            'p_astro_histogram_by_bin=ligo.p_astro_utils:histogram_by_bin',
            'p_astro_compute_means=ligo.p_astro_utils:compute_counts_mean'
        ]
    }
)
