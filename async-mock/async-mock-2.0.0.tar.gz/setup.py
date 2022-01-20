from distutils.core import setup
setup(
  name='async-mock',
  version='2.0.0',
  description='asyncio mocker builder library',
  author='Christopher Brichford',
  author_email='chrisb@farmersbusinessnetwork.com',
  keywords=['testing'],  # arbitrary keywords
  classifiers=['License :: OSI Approved :: BSD License'],
  install_requires=[],
  packages=[
        'async_mock'
    ],
  python_requires='>=3.8',
)
