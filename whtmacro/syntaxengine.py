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
    func        : build in function
    value       : single value
    string      : sequence value
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
        return conv.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"
                ).replace(" ","&nbsp;").replace("\n","<br />")
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
# Base: build-in function block
class SyntElemFunc(SyntElem):
    def __str__(me):
        return "".join(("<span class=\"synt-fnc\">",me.shiftHTML(me.data),"</span>"))
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

# Syntax rule parse
class SyntRule(object):
    def __init__(me,rulelist=None,default=SyntElemNosynt):
        me._allrule = [(re.compile(i[0]),i[1]) for i in rulelist] if rulelist else None
        me._defaultElement = default
    # generate parser-iterator of rule
    def __call__(me,prevObj):
        def iterSearching(substr): # Search element parse
            next_parser = me._allrule
            while True:
                if not substr: break
                all_result = [i for i in filter(
                            lambda b: b[0], map(
                                lambda a: (a[0].search(substr),a[0],a[1]), next_parser))]
                if not all_result: break
                next_parser = [(i[1],i[2]) for i in all_result]
                all_result.sort(key=lambda x: x[0].start())
                choose,parser,elemtype = all_result[0]
                if choose.start() > 0: yield substr[0:choose.start()]
                yield elemtype(choose.group(0))
                substr = substr[choose.end():]
            if substr: yield substr
        def iterLang(langObj): # Iterate element tree
            for obj in langObj:
                if not obj: continue
                if isinstance(obj,SyntElem):
                    yield obj
                elif not me._allrule:
                    yield me._defaultElement(obj)
                else:
                    for sp in iterSearching(obj): yield sp
        return iterLang(prevObj)

# Base: regular parse syntax
class SyntTreeParser(SyntTree):
    # Define your rule in a list named "RULE". the rule must be type of "SyntRule"
    RULE = []
    # Create parse iterator
    def parseTree(me,langStr):
        iterObj = [langStr]
        for p in me.RULE:
            iterObj = p(iterObj)
        return SyntRule()(iterObj)

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
