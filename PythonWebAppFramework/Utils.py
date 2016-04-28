# -*- coding: utf-8 -*-
import functools

def iter_wraper(func):
    functools.wraps(func)

    def _wraper(*args, **kwargs):
        result = func(*args, **kwargs)
        if hasattr(result, '__iter__'):
            print 'Yes! It\'s iterable!'
            if isinstance(result, list) or isinstance(result, tuple):
                return iter(result)
            return result
        else:
            print 'Convert result to iterable!'
            if isinstance(result, basestring):
                print 'Origin result is basestring!'
                return iter([result])
            else:
                return iter(result)

    return _wraper
