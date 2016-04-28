# -*- coding: utf-8 -*-
"""
a simple template engine

usage:
    import template
    template.render(<html_page>, <kwargs>)
"""
import os
import re

base_dir = os.path.dirname(os.path.abspath(__file__))


class Template(object):
    def __init__(self, filename, **kwargs):
        with open(os.path.join(base_dir, filename)) as f:
            self.page = f.read()
        if len(self._vars):
            self._sub_vars(**kwargs)

    @property
    def _vars(self):
        """
        find all the {{ vars }} in template html files
        """
        return re.findall(r"\{\{\s*(\S+)\s*\}\}", self.page)

    def _sub_vars(self, **kwargs):
        assert len(kwargs) == len(set(self._vars)), "args length error"
        for var, val in kwargs.iteritems():
            self.page = re.sub("\{\{\s*" + var + "\s*\}\}", val, self.page)

    def __str__(self):
        return self.page

    def __len__(self):
        return len(self.page)


def template():
    return [t for t in os.listdir(base_dir) if not t.startswith('__init__.')]


def render(template_name, **kwargs):
    if template_name not in template():
        raise IOError('Template not found')
    return Template(template_name, **kwargs)


def main():
    pass


if __name__ == '__main__':
    main()
