from setuptools import setup, find_packages

with open('README.rst', 'r') as fh:
    long_description = fh.read()

setup(
    name='deepGreen',
    version='0.1.3',
    description='A tree-ring width model based on deep learning algorithms',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Feng Zhu, Andong Hu, Michael N. Evans',
    author_email='fzhu@nuist.edu.cn, andong.hu@cwi.nl, mnevans@umd.edu',
    url='https://github.com/fzhu2e/deepGreen',
    packages=find_packages(),
    license='BSD 3-Clause license',
    keywords='Proxy System Modeling, Tree-ring Width, Deep Learning',
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    install_requires=[
        'scikit-learn',
        'skorch',
        'seaborn',
        'p2k',
        'pandas < 1.4.0',
    ],
)
