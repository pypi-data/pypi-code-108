from distutils.core import setup
from setuptools import find_packages
import os

pwd = os.path.dirname(__file__)
with open(os.path.join(pwd, 'README.md'), encoding='utf-8') as f:
  README = f.read()


setup(name='SimilarNeuron',  # 包名
      version='0.0.2-dev',  # 版本号
      description='A similar-neuron system in Python world.',
      long_description=README,
      ong_description_content_type='text/markdown',
      author='ShengXin Lu',
      author_email='luxuncang@qq.com',
      url='https://github.com/luxuncang/similar-neuron',
      install_requires=['pydantic'],
      license='MIT',
      packages=find_packages(),
      include_package_data = True,
      platforms=["all"],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Topic :: Software Development :: Libraries'
      ],
      )