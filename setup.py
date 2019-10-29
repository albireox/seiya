#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2019-10-29
# @Filename: setup.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from distutils.core import setup

import numpy

from Cython.Build import cythonize
from setuptools.extension import Extension


global setup_kwargs


extensions = [
    Extension('seiya.cube.cubify',
              ['seiya/cube/cubify.pyx'],
              include_dirs=[numpy.get_include()])
]


setup_kwargs = {}
setup_kwargs.update({'ext_modules': cythonize(extensions, annotate=True)})


setup(**setup_kwargs)
