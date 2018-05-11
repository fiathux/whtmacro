# -*- coding: utf-8 -*-

'''
Wonderland HTML file template
Low level Markdown engine
------------------------------
Fiathu Su(fiathux@gmail.com)
2015-2018
'''

from whtmacro import htescape

# HTML conetent translator
def HTMLTanslator(tag, attr, contentgen):
    attr2list = lambda attr: " ".join(
            "%s=\"%s\"" % (htescape.escape_enc(k),htescape.escape_enc(v)) for k,v in attr.items())
    if not contentgen:
        return "<%s %s/>" % (tag, attr2list(attr))
    else:
        return "<%s %s>%s</%s>" % (tag, attr2list(attr), "".join(contentgen), tag)

# basic markdown parse element
class mdStack(object):
    LAYERS = []

    def __init__(me, master, pcontent, nextstr):
        me._masterInstance = master
        me._parseContent = pcontent
        
    # next element factory
    def __iter__(me):
        def iterStack():
            nextContent = me._subcontent(nextstr)
            if nextContent:
                for c in nextContent:
                    yield c
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

class titleLayer(mdStack):pass

