from setuptools import setup

setup(name='dassana',
      version='0.2.3',
      description='Dassana common data ingestion functions',
      url='https://github.com/dassana-io/dassana-python',
      author='Dassana',
      author_email='support@dassana.io',
      license='MIT',
      packages=['dassana'],
      install_requires=[
          'certifi',
          'requests',
          'urllib3'
      ],
      zip_safe=False)