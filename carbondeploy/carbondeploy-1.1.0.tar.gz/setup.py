from setuptools import setup

setup(name='carbondeploy',
      version='1.1.0',
      description='Library for deploying Jupyter notebooks.',
      url='https://www.carbondeploy.com/',
      author='Michael Lucy',
      author_email='michaelglucy@gmail.com',
      license='MIT',
      packages=['carbondeploy'],
      zip_safe=True,

      install_requires=[
          'requests>=2.24.0',
          'cloudpickle==2.0.0',
          'importlib-metadata>=4.8.3',
          'tqdm>=4.62.2',
      ],
      python_requires='>=3',
)
