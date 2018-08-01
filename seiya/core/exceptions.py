# !usr/bin/env python
# -*- coding: utf-8 -*-
#
# Licensed under a 3-clause BSD license.
#
# @Author: Brian Cherinka
# @Date:   2017-12-05 12:01:21
# @Last modified by:   Brian Cherinka
# @Last Modified time: 2017-12-05 12:19:32

from __future__ import print_function, division, absolute_import


class SeiyaError(Exception):
    """A custom core Seiya exception"""

    def __init__(self, message=None):

        message = 'There has been an error' \
            if not message else message

        super(SeiyaError, self).__init__(message)


class SeiyaNotImplemented(SeiyaError):
    """A custom exception for not yet implemented features."""

    def __init__(self, message=None):

        message = 'This feature is not implemented yet.' \
            if not message else message

        super(SeiyaNotImplemented, self).__init__(message)


class SeiyaAPIError(SeiyaError):
    """A custom exception for API errors"""

    def __init__(self, message=None):
        if not message:
            message = 'Error with Http Response from Seiya API'
        else:
            message = 'Http response error from Seiya API. {0}'.format(message)

        super(SeiyaAPIError, self).__init__(message)


class SeiyaApiAuthError(SeiyaAPIError):
    """A custom exception for API authentication errors"""
    pass


class SeiyaMissingDependency(SeiyaError):
    """A custom exception for missing dependencies."""
    pass


class SeiyaWarning(Warning):
    """Base warning for Seiya."""


class SeiyaUserWarning(UserWarning, SeiyaWarning):
    """The primary warning class."""
    pass


class SeiyaSkippedTestWarning(SeiyaUserWarning):
    """A warning for when a test is skipped."""
    pass


class SeiyaDeprecationWarning(SeiyaUserWarning):
    """A warning for deprecated features."""
    pass
