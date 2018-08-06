#cython: boundscheck=False, wraparound=False, nonecheck=False

from libc.math cimport exp, sqrt

import numpy
cimport numpy


DTYPE = numpy.float32
ctypedef numpy.float32_t DTYPE_t


def cubify(DTYPE_t [:, :] flux, DTYPE_t [:, :] ivar, DTYPE_t [:, :] xpos, DTYPE_t [:, :] ypos,
           cube_shape, DTYPE_t pixel_size=0.5, DTYPE_t wsigma=0.7, DTYPE_t rlimit=1.6):
    r"""Reconstructs a datacube from RSS arrays using the Shepard's algorithm.

    This function follows the approach to cube reconstruction used by MaNGA
    (see `Law et al. 2016 <http://bit.ly/2M2TmsM>`__). In short, it applies a
    Shepard's algorithm in which the matrix of weights follows a Gaussian
    kernel but sets an upper limit to the contribution of a fibre to a point in
    the grid (``rlimit``). Mathematically,

    .. math::

        w[i,j] = b[i]{\rm exp}\left(-0.5\dfrac{r[i,j]^2}{\sigma^2} \right)

    where :math:`r[i,j]=\sqrt{(x[i]-X[j])^2+(y[i]-Y[j])^2}` is the distance
    from the :math:`ith` fibre to the :math:`jth` point in the cube grid,
    :math:`\sigma` is the exponential scale length, and `b[i]` is zero if the
    inverse variance for fibre :math:`i` is zero, otherwise one. We make
    :math:`w[i,j]=0` for all :math:`r[i,j]>r_{\rm lim}`. For MaNGA,
    :math:`\sigma=0.7\,{\rm arcsec}` and
    :math:`r_{\rm lim}=1.6\,{\rm arcsec}`. The weights are normalised as

    .. math::

        W[i,j] = \dfrac{w[i,j]}{\sum^{N}_{i=1}w[i,j]}

    where we make :math:`W[i,j]=0` if :math:`w[i,j]=0` for all :math:`i`. The
    flux for the cube is then calculated as :math:`F=\alpha W^{T}\times f`
    where :math:`f` is the input flux for each fibre and
    :math:`\alpha=1/(4\pi)` accounts for the conversion from flux per unit of
    area to flux per unit spaxel area.

    The grid is constructed based on the input ``cube_shape``, which determines
    the number of elements in the x and y dimensions, and the pixel size. The
    first element in the grid is always :math:`-cube\_shape \times pixel\_size`
    and the last one :math:`(cube\_shape - 1) \times pixel\_size`.

    If the input ``flux`` and ``ivar`` to this function originate from a MaNGA
    RSS file (e.g., via the `~seiya.cube.manga_rss_to_cube` function), the
    output datacube will be almost identical to the MaNGA DRP 3D cubes. The
    small disparities are due to the DRP slightly different handling of masked
    RSS values. In average, 99.5% of the values in the produced cube are
    identical to the ones produced by the DRP within a relative tolerance of
    :math:`10^{-5}`. Only :math:`0.004\%` of the values differ by more than
    :math:`10^{-3}` (relative).

    This version assumes that all the inputs and outputs are 32-bit float.

    Parameters
    ----------
    flux : `~numpy.ndarray`
        The flux RSS array in which the first dimension is the fibre and the
        second is the wavelength.
    ivar : `~numpy.ndarray`
        As ``flux`` but for the inverse variance.
    xpos : `~numpy.ndarray`
        As ``flux`` but for the x position of the fibre at a given wavelength
        with respect to the nominal centre of the IFU.
    ypos : `~numpy.ndarray`
        Same as ``xpos`` but for the y position.
    cube_shape : tuple
        A tuple with two elements indicating the number of spaxels in the x and
        y directions for the reconstructed cube.
    pixel_size : float
        The size of each spaxel, in arcsec. Defaults to 0.5 arcsec, the value
        used by MaNGA.
    wsigma : float
        The exponential scale length for the Shepard's kernel. Defaults to
        0.7 arcsec, the value used by MaNGA.
    rlimit : float
        The cut-off distance at which a fibre does not contribute to the
        datacube grid. Defaults to 1.6 arcsec, the value used by MaNGA.

    Returns
    -------
    datacube : `~numpy.ndarray`
        A reconstructed 3D datacube in which the first dimension is wavelength,
        second is y, and third is x.

    """

    # Define array shapes and several indexing variables
    cdef Py_ssize_t iwave, ifibre, ii, jj, kk, idx
    cdef DTYPE_t fibre_xpos, fibre_ypos
    cdef DTYPE_t X_test, Y_test

    cdef Py_ssize_t nfibres = flux.shape[0]
    cdef Py_ssize_t nwave = flux.shape[1]

    # Defines some constants that we'll use later
    cdef DTYPE_t alpha = 1. / (4. * numpy.pi)
    cdef DTYPE_t exp_coeff = -0.5 / wsigma**2
    cdef DTYPE_t rlimit2 = rlimit**2
    cdef DTYPE_t window_seach_size = rlimit + pixel_size

    # Assigns the shape of the grid from the input tuple.
    cdef Py_ssize_t X_shape, Y_shape
    X_shape, Y_shape = cube_shape

    # Creates the array of positions on the grid, in x and y.
    cdef DTYPE_t [:] X_range = numpy.arange(-X_shape * pixel_size / 2.,
                                            X_shape * pixel_size / 2.,
                                            pixel_size, dtype=DTYPE)
    cdef DTYPE_t [:] Y_range = numpy.arange(-Y_shape * pixel_size / 2.,
                                            Y_shape * pixel_size / 2.,
                                            pixel_size, dtype=DTYPE)

    # Variables for the different steps of the computation.
    cdef DTYPE_t [:] F_j = numpy.empty(Y_shape * X_shape, dtype=DTYPE)
    cdef DTYPE_t [:, :] w_ij
    cdef DTYPE_t r2_ij, w_sum

    # The final datacube.
    cdef DTYPE_t [:, :, :] F_ijw = numpy.empty((nwave, Y_shape, X_shape), dtype=DTYPE)

    # Loop over each one of the wavelength planes.
    for iwave in range(nwave):

        # Set the weights for this wavelength to zero.
        w_ij = numpy.zeros((nfibres, X_shape * Y_shape), dtype=DTYPE)

        # Calculate the contribution of each fibre to the weights.
        for ifibre in range(nfibres):

            # If the ivar for this fibre and wavelength is zero, this fibre
            # does not contribute, so skip.
            if ivar[ifibre, iwave] == 0:
                continue

            # Measured positions of this fibre for this wavelength.
            fibre_xpos = xpos[ifibre, iwave]
            fibre_ypos = ypos[ifibre, iwave]

            # Loop over each one of the elements in the grid.
            for ii in xrange(X_shape):

                X_test = X_range[ii]  # X value in the grid.

                # If the distance from X_test and fibre_xpos is larger than
                # rlimit plus some padding, skip this grid point since the
                # fibre does not contribute. We'll do the same with Y_test.
                if (X_test < (fibre_xpos - window_seach_size) or
                        X_test > (fibre_xpos + window_seach_size)):
                    continue

                for jj in xrange(Y_shape):

                    Y_test = Y_range[jj]

                    if (Y_test < (fibre_ypos - window_seach_size) or
                            Y_test > (fibre_ypos + window_seach_size)):
                        continue

                    # Calculate the square of the distance between the grid
                    # point and the fibre position. If it's > rlimit, skip.
                    r2_ij = (X_test - fibre_xpos)**2 + (Y_test - fibre_ypos)**2
                    if r2_ij > rlimit2:
                        continue

                    # Use a Gaussian kernel to determine the contribution of
                    # the fibre to to this point on the grid.
                    w_ij[ifibre, ii * X_shape + jj] += exp(exp_coeff * r2_ij)

        # Normalise the weights and calculate the flux for each
        # point on the grid.
        for jj in xrange(X_shape * Y_shape):

            w_sum = 0.0
            F_j[jj] = 0.0

            # Calculate the sum of all the weights for this point on the grid.
            for ii in xrange(nfibres):
                w_sum += w_ij[ii, jj]

            # If the weights are zero, skip.
            if w_sum == 0.0:
                continue

            # Calculate the product of the matrix between the weights and the
            # flux for this point on the grid.
            for ii in xrange(nfibres):
                F_j[jj] += alpha * w_ij[ii, jj] / w_sum * flux[ii, iwave]

        # Reshape F_j to a square grid and store the value for this wavelength
        # plane.
        for ii in xrange(X_shape):
            for jj in xrange(Y_shape):
                F_ijw[iwave, jj, ii] = F_j[X_shape * ii + jj]

    return F_ijw
