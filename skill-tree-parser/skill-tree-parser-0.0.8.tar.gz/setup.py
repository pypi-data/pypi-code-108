#!/usr/bin/env python

from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(name="skill-tree-parser",
      version="0.0.8",
      description="CSDN Skill Tree Parser",
      long_description=long_description,
      long_description_content_type='text/markdown',
      author="Liu Xin",
      author_email="liuxin@csdn.net",
      url="https://gitcode.net/csdn/skill_tree_parser",
      license="MIT",
      packages=["skill_tree", "skill_tree.exercises"],
      package_dir={
          "skill_tree": "src/skill_tree",
          "skill_tree.exercises": "src/skill_tree/exercises"
      },
      install_requires=[
          "pyparsec",
          "GitPython"
      ],
      classifiers=[
          "Topic :: Utilities",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3 :: Only",
          "License :: OSI Approved :: MIT License"
      ])
