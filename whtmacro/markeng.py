# -*- coding: utf-8 -*-

'''
Wonderland HTML file template
Low level Markdown engine
------------------------------
Fiathu Su(fiathux@gmail.com)
2015-2018
'''

import re
from whtmacro import htescape

# HTML conetent translator
def HTMLTanslator(tag, attr, contentgen):
    attr2list = lambda attr: " ".join(
            "%s=\"%s\"" % (htescape.escape_enc(k),htescape.escape_enc(v)) for k,v in attr.items())
    if not contentgen:
        return "<%s %s/>" % (tag, attr2list(attr))
    else:
        return "<%s %s>%s</%s>" % (tag, attr2list(attr), "".join(contentgen), tag)

# content line provider
class contentLine(object):
    # roll back line
    class CLRollBack(Exception):pass
    def __init__(me, content):
        content = content.replace("\r\n","\n").replace("\r","\n")
        me._lines = content.split("\n")
        me._index = 0
        me._withstack = []
    def __iter__(me):
        return me
    def __next__(me):
        if me._index >= len(me._lines):
            raise StopIteration()
        line = me._lines[me._index]
        me._index = me._index + 1 
        return line
    def __enter__(me):
        me._withstack.append(me._index)
    def __exit__(me, exc_type, exc_val, traceback):
        if exc_type is not None:
            me._index = me._withstack.pop()
        else:
            me._withstack.pop()

# basic markdown parse element
class mdStack(object):
    LAYERS = []

    def __init__(me, master, pcontent, nextstr):
        me._masterInstance = master
        me._parseContent = pcontent
        me._env = {}
    # next element factory
    def __iter__(me):
        def iterStack():
            nextContent = me._subcontent(nextstr)
            if nextContent:
                for c in nextContent:
                    yield c
        return iterStack()
    # output inner content
    def __str__(me):
        return me.content
    # report instance
    def __repr__(me):
        return "<%s> at %s" % (me.__name__, repr(me._masterInstance))
    # parse sub-content. overwrite for process sub content
    def _subcontent(me, content):
        if not content: return None
        def contentiter():
            current = content
            for l in LAYERS:
                if current is None: break
                ret = l.parse(content)
                if ret:
                    creator, current = ret
                    yield lambda: creator(me)
                    continue
            if current: yield current
        return contentiter()
    # element factory. overwrite for new parser. return None while no sub-item parse
    @classmethod
    def parse(c, content):
        def export(master):
            return c(master, content, None)
        return export, None

class titleLayer(mdStack):
    LAYERS = []
    P_SHARP = re.compile("(^|\\s*\n)(#{1,6} +([^\n]+))")
    @classmethod
    def parse(c, content):
        pass

