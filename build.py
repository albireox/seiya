#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2018-07-31
# @Filename: setup.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import numpy

from Cython.Build import cythonize
from setuptools.extension import Extension


extensions = [
    Extension('seiya.cube.cubify', ['seiya/cube/cubify.pyx'], include_dirs=[numpy.get_include()])
]


def build(setup_kwargs):
    """This function is mandatory in order to build the extensions."""

    setup_kwargs.update({'ext_modules': cythonize(extensions, annotate=True)})
