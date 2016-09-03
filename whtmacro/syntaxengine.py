# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re
import whtmacro

'''
Default syntax elements
    keyword     : key word
    symbol      : operator-symbol
    comment     : comment string
    type        : data type
    value       : number value
    string      : string
    dsl         : domain specified language
    nosynt      : no syntax hi-light
'''

SYNTAX_PARESER = {}

# Syntax element prototype{{{

# Base: syntax element
class SyntElem(object):
    def __init__(me,langStr):
        me.data = langStr
    def __str__(me):
        return me.shiftHTML(me.data)
    @staticmethod
    def shiftHTML(conv):
        return conv.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace(" ","&nbsp;").replace("\n","<br />")
# Base: no syntax block
class SyntElemNosynt(SyntElem):pass
# Base: key word block
class SyntElemKeyWord(SyntElem):
    def __str__(me):
        return "".join(("<span class=\"synt-kw\">",me.shiftHTML(me.data),"</span>"))
# Base: symbol block
class SyntElemSymbol(SyntElem):
    def __str__(me):
        return "".join(("<span class=\"synt-syb\">",me.shiftHTML(me.data),"</span>"))
# Base: comment block
class SyntElemComment(SyntElem):
    def __str__(me):
        return "".join(("<span class=\"synt-cmt\">",me.shiftHTML(me.data),"</span>"))
# Base: type block
class SyntElemType(SyntElem):
    def __str__(me):
        return "".join(("<span class=\"synt-typ\">",me.shiftHTML(me.data),"</span>"))
# Base: value block
class SyntElemValue(SyntElem):
    def __str__(me):
        return "".join(("<span class=\"synt-val\">",me.shiftHTML(me.data),"</span>"))
# Base: string block
class SyntElemStr(SyntElem):
    def __str__(me):
        return "".join(("<span class=\"synt-str\">",me.shiftHTML(me.data),"</span>"))
# Base: domain specified language block
class SyntElemDSL(SyntElem):
    def __str__(me):
        return "".join(("<span class=\"synt-dsl\">",me.shiftHTML(me.data),"</span>"))

# Base: syntax tree node
class SyntTree(SyntElem):
    def __init__(me,langStr):
        me.data = me.parseTree(langStr)
    def parseTree(me,langStr):
        return [SyntElemNosynt(langStr)]
    def __str__(me):
        return "".join(map(lambda a:"%s" % a, me.data))

# Base: regular parse syntax
class SyntTreeParser(SyntTree):
    '''
    Define your parse regular in the list that named "RANG".
    Item of "RANG" format like this:
    [
        (regular expression,element type base as SyntElem),
        ...
    ]
    '''
    RANG = []
    # Create parse iterator
    def parseTree(me,langStr):
        def iterElement(inIter,parse,elemType):
            for its in inIter:
                if isinstance(its,SyntElem):
                    yield its
                elif not parse:
                    if (its):
                        yield elemType(its)
                else:
                    start = 0
                    for parseElem in parse.finditer(its):
                        yield its[start:parseElem.start()]
                        yield elemType(parseElem.group(0))
                        start = parseElem.end()
                    yield its[start:]
        iterObj = [langStr]
        for p,elem in me.RANG:
            iterObj = iterElement(iterObj,re.compile(p),elem)
        return iterElement(iterObj,None,SyntElemNosynt)

# Prepare HTML text
class SyntTreePreHTML(SyntTree):
    class SyntElemPerHTML(SyntElem):
        @staticmethod
        def shiftHTML(conv):
            return conv.replace(" ","&nbsp;").replace("\n","<br />")
    def parseTree(me,langStr):
        return [me.SyntElemPerHTML(langStr)]
#}}}

# Syntax parser decorator
def decoRegSyntax(name):
    def setDecorate(func):
        SYNTAX_PARESER[name] = func
        return func
    return setDecorate

# text-plane syntax
@decoRegSyntax("txt")
def synt_text(langStr):
    return "".join(("<pre class=\"lang-txt\">","%s" % SyntTree(langStr),"</pre>"))

# Prepare HTML text syntax
@decoRegSyntax("pre-html")
def synt_prehtml(langStr):
    return "".join(("<pre class=\"lang-prehtml\">","%s" % SyntTreePreHTML(langStr) ,"</pre>"))

class ExcSyntLang(whtmacro.ExcWHTBase):
    def __init__(me,lang):
        me.message = "Syntax hi-light unknow language [%s] in %s" % (lang,me.doc_pos())

# Plugins: syntax hi-light
@whtmacro.decoOptPart("syntax")
def opt_include(param):
    if len(param) < 2:
        raise whtmacro.ExcCMDParam()
    if param[0] not in SYNTAX_PARESER:
        raise ExcSyntLang(param[0])
    rootSynt = SYNTAX_PARESER[param[0]]
    return "".join(map(lambda a: rootSynt(a[0]),whtmacro.iterFile(param[1:])))
