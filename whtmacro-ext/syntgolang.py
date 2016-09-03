# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re
from whtmacro import syntaxengine

# Note {{{
'''
there are all operator list from offecial document. I convert it to regular expression with
following codes:
-----------------------
a = [
        "+","&","+=","&=","&&","==","!=","(",")","-","|","-=","|=","||","<","<=",
        "[","]","*","^","*=","^=","<-",">",">=","{","}","/","<<","/=","<<=","++",
        "=",":=",",",";","%",">>","%=",">>=","--","!","...",".",":","&^","&^="
        ]
a.sort(key=lambda c:len(c),reverse=True)
def spconv(s):
    sp = ["\\",".","^","$","*","+","?","{","}","[","]","(",")","|"]
    for psp in sp:
        s = s.replace(psp,"\\"+psp)
    return s

b = map(lambda y:y.replace("\\","\\\\"), map(lambda x: spconv(x) , a))
print("(%s)" % "|".join(b))
=======================

Key word generate with following codes:
-----------------------
a = [
        "break","default","func","interface","select","case","defer","go","map","struct",
        "chan","else","goto","package","switch","const","fallthrough","if",
        "range","type","continue","for","import","return","var"
        ]
print("((?<=[^a-zA-Z0-9_\.])|^)(%s)($|(?=[^a-zA-Z0-9_\.]))" % "|".join(a))
=======================

Type generate with following codes:
-----------------------
a = [
        "int","uint","int8","int16","int32","int64","uint8","uint16","uint32","uint64",
        "rune","float32","float64","complex64","complex128","byte","string","boolean"
        ]
print("((?<=[^a-zA-Z0-9_\.])|^)(%s)($|(?=[^a-zA-Z0-9_\.]))" % "|".join(a))
'''
#}}}

# Golang syntax tree
class SyntTreeGolang(syntaxengine.SyntTreeParser):
    RANG = [
            ("/\\*.*?\\*/", syntaxengine.SyntElemComment),
            ("//.*?(?=\n)", syntaxengine.SyntElemComment),
            ("\"((\\\\\\\\|\\\\\")|[^\"])*\"", syntaxengine.SyntElemStr),
            ("'((\\\\\\\\|\\\\')|[^'])*'", syntaxengine.SyntElemStr),
            ("(?<=[^a-zA-Z0-9_\.])([0-9]+((\.[0-9]*)?([eE][\+-]?[0-9]+)?i?)|\.[0-9]+([eE][\+-]?[0-9]+)?i?|0x[0-9a-fA-F]+)($|(?=[^a-zA-Z0-9_\.]))", syntaxengine.SyntElemValue),
            ("(<<=|>>=|\\.\\.\\.|&\\^=|\\+=|&=|&&|==|!=|-=|\\|=|\\|\\||<=|\\*=|\\^=|<-|>=|<<|/=|\\+\\+|:=|>>|%=|--|&\\^|\\+|&|\\(|\\)|-|\\||<|\\[|\\]|\\*|\\^|>|\\{|\\}|/|=|,|;|%|!|\\.|:)", syntaxengine.SyntElemSymbol),
            ("((?<=[^a-zA-Z0-9_\.])|^)(break|default|func|interface|select|case|defer|go|map|struct|chan|else|goto|package|switch|const|fallthrough|if|range|type|continue|for|import|return|var)($|(?=[^a-zA-Z0-9_\.]))", syntaxengine.SyntElemKeyWord),
            ("((?<=[^a-zA-Z0-9_\.])|^)(int|uint|int8|int16|int32|int64|uint8|uint16|uint32|uint64|rune|float32|float64|complex64|complex128|byte|string|boolean)($|(?=[^a-zA-Z0-9_\.]))", syntaxengine.SyntElemType)
            ]
    

# text-plane syntax
@syntaxengine.decoRegSyntax("golang")
def synt_golang(langStr):
    return "".join(("<pre class=\"lang-go\">","%s" % SyntTreeGolang(langStr),"</pre>"))
