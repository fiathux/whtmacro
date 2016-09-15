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
a = ["lambda","or","and","not","in","not in","is","is not","|","^","&","<<",">>","+","-","*","/","//","%","~","**",":"]
a.sort(key=lambda c:len(c),reverse=True)
def spconv(s):
    sp = ["\\",".","^","$","*","+","?","{","}","[","]","(",")","|"]
    for psp in sp:
        s = s.replace(psp,"\\"+psp)
    return s

b = map(lambda y:y.replace("\\","\\\\").replace(" "," +"), map(lambda x: spconv(x) , a))
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
    RULE = [
            syntaxengine.SyntRule([
                ("/\\*(.|\\s)*?\\*/", syntaxengine.SyntElemComment),
                ("//.*?(?=\\n)", syntaxengine.SyntElemComment),
                ("\"((\\\\\\\\|\\\\\")|[^\"])*\"", syntaxengine.SyntElemStr),
                ("'((\\\\\\\\|\\\\')|[^'])*'", syntaxengine.SyntElemStr)
                ]),
            syntaxengine.SyntRule([("(?<=[^a-zA-Z0-9_\.])([0-9]+((\.[0-9]*)?([eE][\+-]?[0-9]+)?i?)|\.[0-9]+([eE][\+-]?[0-9]+)?i?|0x[0-9a-fA-F]+)($|(?=[^a-zA-Z0-9_\.]))", syntaxengine.SyntElemValue)]),
            syntaxengine.SyntRule([("(?<=[^a-zA-Z0-9_\.])true|false|nil($|(?=[^a-zA-Z0-9_\.]))", syntaxengine.SyntElemValue)]),
            syntaxengine.SyntRule([("(<<=|>>=|\\.\\.\\.|&\\^=|\\+=|&=|&&|==|!=|-=|\\|=|\\|\\||<=|\\*=|\\^=|<-|>=|<<|/=|\\+\\+|:=|>>|%=|--|&\\^|\\+|&|\\(|\\)|-|\\||<|\\[|\\]|\\*|\\^|>|\\{|\\}|/|=|,|;|%|!|\\.|:)", syntaxengine.SyntElemSymbol)]),
            syntaxengine.SyntRule([("((?<=[^a-zA-Z0-9_\.])|^)(break|default|func|interface|select|case|defer|go|map|struct|chan|else|goto|package|switch|const|fallthrough|if|range|type|continue|for|import|return|var)($|(?=[^a-zA-Z0-9_\.]))", syntaxengine.SyntElemKeyWord)]),
            syntaxengine.SyntRule([("((?<=[^a-zA-Z0-9_\.])|^)(int|uint|int8|int16|int32|int64|uint8|uint16|uint32|uint64|rune|float32|float64|complex64|complex128|byte|string|boolean)($|(?=[^a-zA-Z0-9_\.]))", syntaxengine.SyntElemType)])
            ]

# Python syntax tree
class SyntTreePython(syntaxengine.SyntTreeParser):
    RULE = [
            syntaxengine.SyntRule([
                ("[rbu]?\"{3}(\"{1,2}[^\"])?((\\\\\\\\|\\\\\"|[^\"]\"{1,2}[^\"])|[^\"])*\"{3}", syntaxengine.SyntElemStr),
                ("[rbu]?'{3}('{1,2}[^'])?((\\\\\\\\|\\\\'|[^']'{1,2}[^'])|[^'])*'{3}", syntaxengine.SyntElemStr),
                ("#.*?(?=\\n)", syntaxengine.SyntElemComment),
                ("[rbu]?\"((\\\\\\\\|\\\\\")|[^\"])*\"", syntaxengine.SyntElemStr),
                ("[rbu]?'((\\\\\\\\|\\\\')|[^'])*'", syntaxengine.SyntElemStr)
                ]),
            syntaxengine.SyntRule([("(?<=[^a-zA-Z0-9_\\.])([0-9]+((\\.[0-9]*)?([eE][\+-]?[0-9]+)?j?)|\\.[0-9]+([eE][\+-]?[0-9]+)?j?|0x[0-9a-fA-F]+)($|(?=[^a-zA-Z0-9_\\.]))", syntaxengine.SyntElemValue)]),
            syntaxengine.SyntRule([("(?<=[^a-zA-Z0-9_\\.])True|False|None($|(?=[^a-zA-Z0-9_\\.]))", syntaxengine.SyntElemValue)]),
            syntaxengine.SyntRule([("(((?<=[^a-zA-Z0-9_\\.])(lambda|not +in|is +not|and|not|or|in|is)(?=[^a-zA-Z0-9_\\.]))|==|!=|>|<|>=|<=|=|,|\\(|\\)|\\[|\\]|\\{|\\}|<<|>>|//|\\*\\*|\\||\\^|&|\\+|-|\\*|/|%|~|:)", syntaxengine.SyntElemSymbol)]),
            syntaxengine.SyntRule([("(?<=\\s|\\.)__(new|init|del|repr|str|lt|le|eq|ne|gt|ge|cmp|rcmp|hash|nonzero|unicode|getattr|setattr|delattr|getattribute|get|set|delete|slots|metaclass|instancecheck|subclasscheck|call|len|getitem|missing|setitem|delitem|iter|reversed|contains|getslice|setslice|delslice|add|sub|mul|floordiv|mod|divmod|pow|lshift|rshift|and|xor|or|div|truediv|radd|rsub|rmul|rdiv|rtruediv|rfloordiv|rmod|rdivmod|rpow|rlshift|rrshift|rand|rxor|ror|iadd|isub|imul|idiv|itruediv|ifloordiv|imod|ipow|ilshift|irshift|iand|ixor|ior|neg|pos|abs|invert|complex|int|long|float|oct|hex|index|coerce|enter|exit)__((?=[^a-zA-Z0-9_\\.])|$)", syntaxengine.SyntElemFunc)]),
            syntaxengine.SyntRule([("((?<=[^a-zA-Z0-9_\\.])|^)(divmod|globals|print|repr|delattr|basestring|hash|dir|all|map|eval|compile|hex|setattr|abs|max|ord|next|help|execfile|any|reversed|reduce|super|sum|sorted|vars|slice|iter|input|reload|round|raw_input|id|callable|oct|ascii|staticmethod|isinstance|cmp|file|issubclass|locals|min|pow|getattr|hasattr|chr|__import__|classmethod|unichr|bool|open|filter|len|format|object|bin|exec|type|enumerate|property|zip)(?=\\s*\()", syntaxengine.SyntElemFunc)]),
            syntaxengine.SyntRule([("((?<=[^a-zA-Z0-9_\\.])|^)(del|from|while|as|elif|global|with|assert|else|if|pass|yield|break|except|import|print|class|exec|in|raise|continue|finally|return|def|for|try|__all__)($|(?=[^a-zA-Z0-9_\\.]))", syntaxengine.SyntElemKeyWord)]),
            syntaxengine.SyntRule([("((?<=[^a-zA-Z0-9_\\.])|^)(int|long|complex|float|str|unicode|bytes|bytearray|memoryview|tuple|list|set|frozenset|dict|range|xrange)($|(?=[^a-zA-Z0-9_\\.]))", syntaxengine.SyntElemType)])
            ]

class SyntTreeJS(syntaxengine.SyntTreeParser):
    class SyntTreeJSImport(syntaxengine.SyntTreeParser):
        RULE = [
                syntaxengine.SyntRule([
                    ("/\\*(.|\\s)*?\\*/", syntaxengine.SyntElemComment),
                    ("//.*?(?=\\n)", syntaxengine.SyntElemComment),
                    ("\"((\\\\\\\\|\\\\\")|[^\"])*\"", syntaxengine.SyntElemStr),
                    ("'((\\\\\\\\|\\\\')|[^'])*'", syntaxengine.SyntElemStr)
                    ]),
                syntaxengine.SyntRule([("(\\{|\\}|\\*|,|;)", syntaxengine.SyntElemSymbol)]),
                syntaxengine.SyntRule([("((?<=[^a-zA-Z0-9_\\.])|^)(import|as|from)($|(?=[^a-zA-Z0-9_\\.]))", syntaxengine.SyntElemKeyWord)])
                ]
    RULE = [
            syntaxengine.SyntRule([
                ("/\\*(.|\\s)*?\\*/", syntaxengine.SyntElemComment),
                ("//.*?(?=\\n)", syntaxengine.SyntElemComment),
                ("\"((\\\\\\\\|\\\\\")|[^\"])*\"", syntaxengine.SyntElemStr),
                ("'((\\\\\\\\|\\\\')|[^'])*'", syntaxengine.SyntElemStr),
                ("/((\\\\\\\\|\\\\/)|[^/])*/", syntaxengine.SyntElemDSL),
                ("(^|(?<=[^a-zA-Z0-9_\\\\.]))(import(?=\\s|\\*|\\{|\"|\'))([^'\"/]|/[^*'\"]|(/\\*(.|\\s)*?\\*/|\"((\\\\\\\\|\\\\\")|[^\"])*\"|'((\\\\\\\\|\\\\')|[^'])*'|//.*?(?=\\n)))*?(;|\\n)",SyntTreeJSImport)
                ]),
            syntaxengine.SyntRule([("(?<=[^a-zA-Z0-9_\\.])([0-9]+((\\.[0-9]*)?([eE][\+-]?[0-9]+)?)|\\.[0-9]+([eE][\+-]?[0-9]+)?|0x[0-9a-fA-F]+)($|(?=[^a-zA-Z0-9_\\.]))", syntaxengine.SyntElemValue)]),
            syntaxengine.SyntRule([("(?<=[^a-zA-Z0-9_\\.])true|true|null|NaN|Infinity($|(?=[^a-zA-Z0-9_\\.]))", syntaxengine.SyntElemValue)]),
            syntaxengine.SyntRule([("((?<=[^a-zA-Z0-9_\\.])|^)(var|let|const|function\\s*\\*|function|=>|yield\\s*\\*|yield|for|if|else|return|switch|case|throw|try|cache|finally|while|with|new|delete|class|get|set)($|(?=[^a-zA-Z0-9_\\.]))", syntaxengine.SyntElemKeyWord)]),
            syntaxengine.SyntRule([("(((?<=[^a-zA-Z0-9_\\.])(in|of|instanceof|typeof)(?=[^a-zA-Z0-9_\\.]))|\\{|\\}|\\[|\\]|\\(|\\)|\\+\\+|\\+|--|-|\\*\\*|\\*|/|%|>>>|>>|<<|>|<|>=|<=|!==|!=|===|==|=|\\|\\||&&|!|&|\\||~|\\^|\\?|:|,|\\.|;)", syntaxengine.SyntElemSymbol)]),
            syntaxengine.SyntRule([("((?<=[^a-zA-Z0-9_\\.])|^)(Number|String|Boolean|Symbol|Object|null|undefined|Function|Array|ArrayBuffer|Date|Error|RegExp|Promise|Generator|JSON)($|(?=[^a-zA-Z0-9_\\.]))", syntaxengine.SyntElemType)]),
            syntaxengine.SyntRule([("((?<=[^a-zA-Z0-9_\\.])|^)(this|super)($|(?=[^a-zA-Z0-9_]))", syntaxengine.SyntElemKeyWord)]),
            syntaxengine.SyntRule([("((?<=[^a-zA-Z0-9_\\.])|^)(decodeURI|encodeURI|decodeURIComponent|encodeURIComponent|escape|eval|isFinite|isNaN|parseFloat|parseInt|unescape|uneval)(?=\\s*\()", syntaxengine.SyntElemFunc)])
            ]

# golang syntax
@syntaxengine.decoRegSyntax("golang")
def synt_golang(langStr):
    return "".join(("<pre class=\"lang-go\">","%s" % SyntTreeGolang(langStr),"</pre>"))

# python syntax
@syntaxengine.decoRegSyntax("python")
def synt_golang(langStr):
    return "".join(("<pre class=\"lang-py\">","%s" % SyntTreePython(langStr),"</pre>"))

# python syntax
@syntaxengine.decoRegSyntax("javascript")
def synt_golang(langStr):
    return "".join(("<pre class=\"lang-js\">","%s" % SyntTreeJS(langStr),"</pre>"))
