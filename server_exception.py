# -*- coding: utf-8 -*-
class ServerException(Exception):
    """
    for internal error reporting
    """


class RequestPathException(ServerException):
    """

    """


class NoHandlerException(ServerException):
    """

    """


class CGIRunException(ServerException):
    """

    """