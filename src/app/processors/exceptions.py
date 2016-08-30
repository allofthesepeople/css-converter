# -*- coding: utf-8 -*-

# Third party
from flask import g


class ValidationError(Exception):
    # pass
    def __init__(self, message):
        try:
            g.errors.append(message)
        except AttributeError:
            g.errors = []
            g.errors.append(message)
        super(ValidationError, self).__init__(message)
