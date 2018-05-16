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
from whtmacro.lines import contentLine

# HTML conetent translator
def HTMLTanslator(tag, attr, contentgen):
    attr2list = lambda attr: " ".join(
            "%s=\"%s\"" % (htescape.escape_enc(k),htescape.escape_enc(v)) for k,v in attr.items())
    if not contentgen:
        return "<%s %s/>" % (tag, attr2list(attr))
    else:
        return "<%s %s>%s</%s>" % (tag, attr2list(attr), "".join(contentgen), tag)

class mdStack(object):
    def __init__(me):
        me.titleLevel = 0
        me.listStack = []
        me.blockState = "content"
        me.tabRow = None
        me.tabCol = None

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

