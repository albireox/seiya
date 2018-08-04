#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2018-07-31
# @Filename: setup.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)
#
# @Last modified by: José Sánchez-Gallego (gallegoj@uw.edu)
# @Last modified time: 2018-08-03 16:41:09


from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import os
import sys

import numpy
from Cython.Build import cythonize
from setuptools import find_packages, setup
from setuptools.extension import Extension


# The NAME variable should be of the format "sdss-seiya".
# Please check your NAME adheres to that format.
NAME = 'seiya'
VERSION = '0.1.0dev'
RELEASE = 'dev' in VERSION


extensions = [
    Extension('seiya.cube.cubify', ['seiya/cube/cubify.pyx'], include_dirs=[numpy.get_include()])
]


def run(packages, install_requires):

    setup(name=NAME,
          version=VERSION,
          license='BSD3',
          description='Cube reconstruction and stacking tools for MaNGA data',
          long_description=open('README.rst').read(),
          author='José Sánchez-Gallego',
          author_email='gallegoj@uw.edu',
          keywords='astronomy software',
          url='https://github.com/albireox/seiya',
          include_package_data=True,
          packages=packages,
          install_requires=install_requires,
          ext_modules=cythonize(extensions, annotate=True),
          scripts=['bin/seiya'],
          classifiers=[
              'Development Status :: 4 - Beta',
              'Intended Audience :: Science/Research',
              'License :: OSI Approved :: BSD License',
              'Natural Language :: English',
              'Operating System :: OS Independent',
              'Programming Language :: Python',
              'Programming Language :: Python :: 3.6',
              'Topic :: Documentation :: Sphinx',
              'Topic :: Software Development :: Libraries :: Python Modules'
          ])


def get_requirements(opts):
    """Get the proper requirements file based on the optional argument"""

    if opts.dev:
        name = 'requirements_dev.txt'
    elif opts.doc:
        name = 'requirements_doc.txt'
    else:
        name = 'requirements.txt'

    requirements_file = os.path.join(os.path.dirname(__file__), name)
    install_requires = [line.strip().replace('==', '>=') for line in open(requirements_file)
                        if not line.strip().startswith('#') and line.strip() != '']

    return install_requires


def remove_args(parser):
    """Remove custom arguments from the parser"""

    arguments = []
    for action in list(parser._get_optional_actions()):
        if '--help' not in action.option_strings:
            arguments += action.option_strings

    for arg in arguments:
        if arg in sys.argv:
            sys.argv.remove(arg)


if __name__ == '__main__':

    # Custom parser to decide whether which requirements to install
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]))
    parser.add_argument('-d', '--dev', dest='dev', default=False, action='store_true',
                        help='Install all packages for development')
    parser.add_argument('-o', '--doc', dest='doc', default=False, action='store_true',
                        help='Install only core + documentation packages')

    # We use parse_known_args because we want to leave the remaining args for distutils
    args = parser.parse_known_args()[0]

    # Get the proper requirements file
    install_requires = get_requirements(args)

    # Now we remove all our custom arguments to make sure they don't interfere with distutils
    remove_args(parser)

    # Have distutils find the packages
    packages = find_packages()

    # Runs distutils
    run(packages, install_requires)
