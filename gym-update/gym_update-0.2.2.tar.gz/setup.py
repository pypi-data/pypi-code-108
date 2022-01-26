#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# -*- coding: utf-8 -*-


import setuptools
from pathlib import Path
#from setuptools import setup
setuptools.setup(name='gym_update',
      version='0.2.2',
      description="A OpenAI Gym Env for continuous control",
      long_description=Path("README.md").read_text(),
      long_description_content_type="text/markdown",
                 author="Claudia Viaro",
                 license="MIT",
      packages=setuptools.find_packages(include="gym_update*"),
      install_requires=['gym']  # And any other dependencies needed
)

