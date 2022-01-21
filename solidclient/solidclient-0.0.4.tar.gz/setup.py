from setuptools import setup

setup(name='solidclient',
      version='0.0.4',
      description='A Solid client in Python',
      url='https://gitlab.com/arbetsformedlingen/individdata/oak/python_solid_client.git',
      author='Fredrik Höllinger',
      author_email='fredrik.hollinger@arbetsformedlingen.se',
      license='MIT',
      packages=['solidclient', 'solidclient.utils'],
      python_requires='>= 3.6',
      )
