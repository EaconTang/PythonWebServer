# -*- coding: utf-8 -*-
class ServerException(Exception):
    """
    for internal error reporting
    """


class WSGIServerException(ServerException):
    """

    """


class SendResponseException(ServerException):
    """

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
