   
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


long_description = """
nidf is a simple, striped down `find` replacement for use on NAS or slow disk drives. Results  may be faster than `find` on SSDs for deep but not shallow searches.'
"""


setup(name="nidf",
      description="nidf",
      long_description=long_description,
      license="MIT",
      version="0.0.3",
      author="Samuel Woodward",
      author_email="sam@woodward.fyi",
      maintainer="Samuel Woodward   ",
      maintainer_email="sam@woodward.fyi",
      url="https://github.com/PyWoody/nidf",
      packages=['nidf'],
      python_requires='>= 3.7',
      classifiers=[
          'Programming Language :: Python :: 3',
      ])

