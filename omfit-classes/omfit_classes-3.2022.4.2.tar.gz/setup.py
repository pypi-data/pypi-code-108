from setuptools import setup
import os

# ======================
# Install `omfit_classes` package
# ======================

os.chdir(os.path.split(os.path.realpath(__file__))[0])

with open('omfit_classes/version') as f:
    version = f.read().strip() + '.2'

with open('README.rst') as f:
    long_description = '\n' + '\n'.join(f.read().strip().split('\n')[2:])

package_data = ['../LICENSE.txt', '../README.rst', '*']
for root, dir, files in os.walk("omfit_classes"):
    if root == 'omfit_classes':
        continue
    if '__pycache__' in root:
        continue
    package_data.append(root[len('omfit_classes') + 1 :] + os.sep + '*')

setup(
    name='omfit_classes',
    version=version,
    description='Classes of OMFIT (One Modeling Framework For Integrated Tasks)',
    long_description=long_description,
    url='https://omfit.io',
    author='OMFIT developers',
    author_email="meneghini@fusion.gat.com",
    classifiers=['Programming Language :: Python :: 3', 'Operating System :: OS Independent', 'License :: OSI Approved :: MIT License'],
    keywords='integrated modeling plasma framework',
    packages=['omfit_classes'],
    package_dir={'omfit_classes': 'omfit_classes'},
    install_requires=[],
    extras_require={},
    package_data={'omfit_classes': package_data},
    license='MIT',
)
