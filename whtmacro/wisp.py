# -*- coding: utf-8 -*-

'''
Wonderland HTML file template
the WISP language module
------------------------------
Fiathu Su(fiathux@gmail.com)
2015-2017
'''

from __future__ import unicode_literals

from whtmacro import sexp

# basic WISP object
class WISPObject(sexp.SElement):pass

class WISPExpression(sexp.SExpression, WISPObject):
    def __init__(me, exp_gen, env, pos = sexp.SPosition(0,0,0,0)):
        super(WISPExpression,me).__init__(exp_gen, env, pos)
    def __call__():
        pass
