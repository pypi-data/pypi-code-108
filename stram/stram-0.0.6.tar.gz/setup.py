from setuptools import setup, find_packages


with open('README.md', 'r') as fh:
    long_description = fh.read()

short_description = (
    'Style TRAnsfer Machine - a package for performing '
    + 'image style transfer using machine learning methods'
)

setup(
    name='stram',
    version='0.0.6',
    author='emilutz',
    author_email='emil.barbutza@gmail.com',
    description=short_description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/forgeai/style2pic.git',
    packages=find_packages(exclude=['scripts*', 'tests*']),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'bunch',
        'numpy',
        'opencv-python',
        'pydot',
        'scipy',
        'static-variables',
        'python-decouple',
        'static-variables',
        'tensorflow==2.7',
        'tensorflow-hub',
        'tensorflow-io',
        'tqdm',
    ],
)
