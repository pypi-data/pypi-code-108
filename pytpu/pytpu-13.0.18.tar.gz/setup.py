# coding: utf-8
"""Setup script for IVA TPU."""
from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

# tmp = find_packages()

setup(name='pytpu',
      packages=['pytpu', 'pytpu.tools', 'pytpu.pytpu', 'pytpu.scripts'],
      # packages=find_packages(),
      version="13.0.18",
      author="Maxim Moroz",
      author_email="m.moroz@iva-tech.ru",
      description="TPU Python API",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="http://git.mmp.iva-tech.ru/tpu_sw/iva_tpu_sdk",
      install_requires=[
            'numpy>=1.14',
      ],
      zip_safe=False,
      python_requires='>=3.6',
      entry_points={
            'console_scripts': [
                'run_get_fps = pytpu.scripts.run_get_fps:main'
            ]
        },
      )
