# -*- coding: utf-8 -*-
import robaccia
import model

def list(environ, start_response):
    rows = model.entry_table.select().execute()
    return robaccia.render(start_response, 'list.html', locals())

def member_get(environ, start_response):
    id = environ['selector.vars']['id']
    row = model.entry_table.select(model.entry_table.c.id==id).execute().fetchone()
    return robaccia.render(start_response, 'entry.html', locals())

def create(environ, start_response):
    pass

def create_form(environ, start_response):
    pass

def member_edit_form(environ, start_response):
    pass

def member_update(environ, start_response):
    pass
