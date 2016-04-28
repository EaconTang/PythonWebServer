# -*- coding: utf-8 -*-
import template
import SimpleHTTPServer


t = "{a}bc"

print template.render("error_page.html", msg="test")