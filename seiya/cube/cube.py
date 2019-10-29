#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2018-07-31
# @Filename: cube.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)
#
# @Last modified by: José Sánchez-Gallego
# @Last modified time: 2019-10-29 00:49:52


import sys

import astropy

from seiya import log
from seiya.cube.cubify import cubify


def manga_rss_to_cube(rss):
    """Creates a datacube from a MaNGA RSS file.

    This is a wrapper around `.cubify` for convenience when using MaNGA
    RSS files. The resulting datacubes have the same shape as a MaNGA cube.

    Parameters
    ----------
    rss : `str` or `astropy.io.fits.HDUList`
        The path to the MaNGA RSS file to use to construct the cube, or an
        `~astropy.io.fits.HDUList` with the same format.

    """

    if isinstance(rss, str):
        rss = astropy.io.fits.open(rss)
    else:
        assert isinstance(rss, astropy.io.fits.HDUList), 'invalid type for rss.'

    flux = rss['FLUX'].data
    ivar = rss['IVAR'].data
    xpos = rss['XPOS'].data
    ypos = rss['YPOS'].data

    # cubify requires that the endianness of the data and the compile match.
    # We check that they are the same here and if not modify the arrays.
    if ((sys.byteorder == 'little' and flux.dtype.byteorder == '>') or
            (sys.byteorder == 'big' and flux.dtype.byteorder == '<')):

        log.warning('changing endianness for input data.', UserWarning)

        flux = flux.byteswap().newbyteorder()
        ivar = ivar.byteswap().newbyteorder()
        xpos = xpos.byteswap().newbyteorder()
        ypos = ypos.byteswap().newbyteorder()

    ifudesign = rss[0].header['IFUDSGN']
    ifusize = int(str(ifudesign)[0:-2])

    if ifusize == 19:
        cube_shape = (34, 34)
    elif ifusize == 127:
        cube_shape = (72, 72)
    else:
        # Fill other sizes later
        raise ValueError(f'ifusize {ifusize} not yet implemented.')

    return cubify(flux, ivar, xpos, ypos, cube_shape)
