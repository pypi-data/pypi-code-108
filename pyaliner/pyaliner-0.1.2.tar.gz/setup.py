from pathlib import Path
from setuptools import setup

setup(name='pyaliner',
      version='0.1.2',
      description='A library for comparing sequential data',
      long_description=(Path(__file__).parent.resolve() / 'README.md').read_text(encoding='utf8'),
      long_description_content_type='text/markdown',
      url='https://github.com/JoseLlarena/pyaliner',
      author='Jose Llarena',
      author_email='jose.llarena@gmail.com',
      license='MIT',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Other Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: Implementation :: CPython',
          'Topic :: Utilities',
          'Topic :: Software Development :: Libraries'
      ],
      keywords='alignment, visualisation',
      packages=['pyaliner'],
      python_requires='>=3.7',
      install_requires=['edlib', 'rich', 'pypey', 'click'],
      extras_require={'test': ['pytest', 'hypothesis']})
