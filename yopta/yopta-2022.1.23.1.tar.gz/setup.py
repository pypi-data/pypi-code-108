from setuptools import setup

long_description = ""
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(name='yopta',
      version='2022.1.23.1',
      author="aqur1n",
      long_description=long_description,
      url=r"https://github.com/aqur1n/yopta.py",
      long_description_content_type = "text/markdown",
      description='Перевод методов, атрибутов и функций на пацанский для python!',
      packages=['yopta'],
      zip_safe=False,
      python_requires='>=3.8.0',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Typing :: Typed',
      ])