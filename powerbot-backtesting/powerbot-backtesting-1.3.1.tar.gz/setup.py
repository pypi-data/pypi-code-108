from setuptools import setup

setup(name='powerbot-backtesting',
      version='1.3.1',
      description="All of PowerBot's backtesting functions in one package",
      url='https://github.com/powerbot-trading/powerbot_backtesting',
      author='PowerBot Trading',
      author_email='techinfo@powerbot-trading.com',
      license='MIT',
      packages=['powerbot_backtesting'],
      package_data={'powerbot_backtesting': ['exceptions/*', 'utils/*', 'models/*']},
      install_requires=[
          'urllib3',
          'certifi',
          'python-dateutil',
          'pandas',
          'plotly',
          'SQLAlchemy',
          'requests',
          'powerbot-client',
          'pydantic',
          'tqdm'],
      python_requires='>= 3.9',
      zip_safe=False,
      long_description_content_type='text/markdown',
      long_description=open('README.md').read()
      )
