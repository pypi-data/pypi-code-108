#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
from setuptools import setup

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='inspqcommun',
    url='https://gitlab.forge.gouv.qc.ca/inspq/commun/python/inspqcommun.git',
    author='Philippe Gauthier',
    author_email='philippe.gauthier@inspq.qc.ca',
    # Needed to actually package something
    packages=['inspqcommun.identity','inspqcommun.userprovisioning','inspqcommun.hl7','inspqcommun.kafka'],
    # Needed for dependencies
    install_requires=['fhirclient==1.0.3','wheel','urllib3','requests','pyjwt','jinja2','PyYAML','ansible>=2.9,<2.10','confluent_kafka','pygelf','six'],
    # *strongly* suggested for sharing
    #version='1.0.4',
    version_command=('git describe', "pep440-git-local"),
    # The license can be anything you like
    license='LiLiQ',
    description='Librairies communes de INSPQ',
    long_description=io.open('README.md', 'r', encoding="utf-8").read(),
)

