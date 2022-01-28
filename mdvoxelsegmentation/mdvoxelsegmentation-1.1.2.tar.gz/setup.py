#!/usr/bin/env python
# -*- coding: utf-8 -*-
import setuptools

setuptools.setup(
    packages=['mdvoxelsegmentation'],
    package_data={'mdvoxelsegmentation': ['vmd_clusters_visualization.vmd']},
    include_package_data=True,
    entry_points = {
        'console_scripts' : ['mdvseg=mdvoxelsegmentation.do_segmentation:main'],
        },
)
