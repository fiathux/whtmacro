# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re
from whtmacro import syntaxengine

# RegExp template {{{

# General rule template
def mkruleTempGeneral(first_parse=""):
    def regexShift(s):
        regex_symb = ["\\",".","^","$","*","+","?","{","}","[","]","(",")","|"]
        for rs in regex_symb:
            s = s.replace(rs,"\\"+rs)
        return s
    def curryLayer1(last_parse=""):
        def curryLayer2(head_parse=""):
            def curryLayer3(tail_parse=""):
                def curryLayer4(element):
                    def curryFinal(*wordlist, **addit):
                        # Addit parameter
                        if "pre_rule" not in addit: addit["pre_rule"] = None
                        if "flow_rule" not in addit: addit["flow_rule"] = None
                        if "re_shift" not in addit: addit["re_shift"] = True
                        wordexpr = "|".join(
                                map(regexShift, wordlist) if addit["re_shift"] else wordlist)
                        if addit["pre_rule"]: wordexpr = addit["pre_rule"] + "|" + wordexpr
                        if addit["flow_rule"]: wordexpr = wordexpr + "|" + addit["flow_rule"]
                        return "".join([ # Combine regexp
                            head_parse, first_parse, "(", wordexpr, ")", last_parse, tail_parse
                            ]),element
                    return curryFinal
                return curryLayer4
            return curryLayer3
        return curryLayer2
    return curryLayer1

# Word templates
mkrulePartLeftWord = mkruleTempGeneral("((?<=[^a-zA-Z0-9_\.])|^)")("(?=[^a-zA-Z0-9_\.])")
mkrulePartRightWord = mkruleTempGeneral("(?<=[^a-zA-Z0-9_\.])")("($|(?=[^a-zA-Z0-9_\.]))")
mkrulePartUniqueWord = mkruleTempGeneral("((?<=[^a-zA-Z0-9_\.])|^)")("($|(?=[^a-zA-Z0-9_\.]))")
# Expression templates
mkrulePartLeftExp = mkruleTempGeneral("((?<=[^a-zA-Z0-9_])|^)")("(?=[^a-zA-Z0-9_\.])")
mkrulePartRightExp = mkruleTempGeneral("(?<=[^a-zA-Z0-9_\.])")("($|(?=[^a-zA-Z0-9_]))")
mkrulePartGeneralExp = mkruleTempGeneral("((?<=[^a-zA-Z0-9_])|^)")("($|(?=[^a-zA-Z0-9_]))")
mkruleTempGeneral("((?<=[^a-zA-Z0-9_])|^)")("($|(?=[^a-zA-Z0-9_]))")

# General element rule
mkruleKeyword = mkrulePartUniqueWord()()(syntaxengine.SyntElemKeyWord)
mkruleSimpType = mkrulePartUniqueWord()()(syntaxengine.SyntElemType)
mkruleClassType = mkrulePartLeftExp()()(syntaxengine.SyntElemType)
mkruleFunc = mkruleTempGeneral(
        "((?<=[^a-zA-Z0-9_\.])|^)")("(?=\\s*\()")()()(syntaxengine.SyntElemFunc)
mkruleSymbol = mkruleTempGeneral()()()()(syntaxengine.SyntElemSymbol)

# }}}

# C syntax tree {{{
class SyntTreeC(syntaxengine.SyntTreeParser):
    CSTY_COMMENT = ("/\\*(.|\\s)*?\\*/", syntaxengine.SyntElemComment)
    CSTY_COMMENT_LINE = ("//.*?(?=\\n)", syntaxengine.SyntElemComment)
    CSTY_STR = ("\"((\\\\\\\\|\\\\\")|[^\"])*\"", syntaxengine.SyntElemStr)
    CSTY_CHAR = ("'((\\\\\\\\|\\\\')|[^'])*'", syntaxengine.SyntElemStr)
    RULE = [
            [
                CSTY_COMMENT,
                CSTY_COMMENT_LINE,
                CSTY_STR,
                CSTY_CHAR
            ],
        ]
#}}}

# Golang syntax tree {{{
class SyntTreeGolang(syntaxengine.SyntTreeParser):
    GOLANG_NUM = (
            "[0-9]+((\.[0-9]*)?([eE][\+-]?[0-9]+)?i?)", # integer or normal float with complex
            "\.[0-9]+([eE][\+-]?[0-9]+)?i?", # simple float with complex
            "0x[0-9a-fA-F]+" # hex integer
            )
    GOLANG_SPECVAL = ("true","false","nil")
    GOLANG_SYMBOL = (
            "<<=", ">>=", "...", "&^=", "+=", "&=", "&&", "==", "!=", "-=", 
            "|=", "||", "<=", "*=", "^=", "<-", ">=", "<<", "/=", "++", 
            ":=", ">>", "%=", "--", "&^", "+", "&", "(", ")", "-", "|", "<", 
            "[", "]", "*", "^", ">", "{", "}", "/", "=", ", ", ";", "%",
            "!", ".", ":"
            )
    GOLANG_KW = (
            "break", "default", "func", "interface", "select", "case", "defer",
            "go", "map", "struct", "chan", "else", "goto", "package", "switch",
            "const", "fallthrough", "if", "range", "type", "continue", "for",
            "import", "return", "var"
            )
    GOLANG_TYPE = (
            "int", "uint", "int8", "int16", "int32", "int64", "uint8", "uint16",
            "uint32", "uint64", "rune", "float32", "float64", "complex64",
            "complex128", "byte", "string", "bool"
            )
    GOStyleType = mkrulePartRightWord()()(syntaxengine.SyntElemType)
    RULE = [
            [
                SyntTreeC.CSTY_COMMENT,
                SyntTreeC.CSTY_COMMENT_LINE,
                SyntTreeC.CSTY_STR,
                SyntTreeC.CSTY_CHAR
            ],
            mkrulePartUniqueWord()()(syntaxengine.SyntElemValue)(*GOLANG_NUM,re_shift=False),
            mkrulePartUniqueWord()()(syntaxengine.SyntElemValue)(*GOLANG_SPECVAL),
            mkruleSymbol(*GOLANG_SYMBOL),
            mkruleKeyword(*GOLANG_KW),
            GOStyleType(*GOLANG_TYPE)
        ]
#}}}

# Python syntax tree {{{
class SyntTreePython(syntaxengine.SyntTreeParser):
    RULE = [
            [
                ("[rbu]?\"{3}(\"{1,2}[^\"])?((\\\\\\\\|\\\\\"|[^\"]\"{1,2}[^\"])|[^\"])*\"{3}", syntaxengine.SyntElemStr),
                ("[rbu]?'{3}('{1,2}[^'])?((\\\\\\\\|\\\\'|[^']'{1,2}[^'])|[^'])*'{3}", syntaxengine.SyntElemStr),
                ("#.*?(?=\\n)", syntaxengine.SyntElemComment),
                ("[rbu]?\"((\\\\\\\\|\\\\\")|[^\"])*\"", syntaxengine.SyntElemStr),
                ("[rbu]?'((\\\\\\\\|\\\\')|[^'])*'", syntaxengine.SyntElemStr)
            ],
            ("(?<=[^a-zA-Z0-9_\\.])([0-9]+((\\.[0-9]*)?([eE][\+-]?[0-9]+)?j?)|\\.[0-9]+([eE][\+-]?[0-9]+)?j?|0x[0-9a-fA-F]+)($|(?=[^a-zA-Z0-9_\\.]))", syntaxengine.SyntElemValue),
            ("(?<=[^a-zA-Z0-9_\\.])True|False|None($|(?=[^a-zA-Z0-9_\\.]))", syntaxengine.SyntElemValue),
            ("(((?<=[^a-zA-Z0-9_\\.])(lambda|not +in|is +not|and|not|or|in|is)(?=[^a-zA-Z0-9_\\.]))|==|!=|>|<|>=|<=|=|,|\\(|\\)|\\[|\\]|\\{|\\}|<<|>>|//|\\*\\*|\\||\\^|&|\\+|-|\\*|/|%|~|:)", syntaxengine.SyntElemSymbol),
            ("(?<=\\s|\\.)__(new|init|del|repr|str|lt|le|eq|ne|gt|ge|cmp|rcmp|hash|nonzero|unicode|getattr|setattr|delattr|getattribute|get|set|delete|slots|metaclass|instancecheck|subclasscheck|call|len|getitem|missing|setitem|delitem|iter|reversed|contains|getslice|setslice|delslice|add|sub|mul|floordiv|mod|divmod|pow|lshift|rshift|and|xor|or|div|truediv|radd|rsub|rmul|rdiv|rtruediv|rfloordiv|rmod|rdivmod|rpow|rlshift|rrshift|rand|rxor|ror|iadd|isub|imul|idiv|itruediv|ifloordiv|imod|ipow|ilshift|irshift|iand|ixor|ior|neg|pos|abs|invert|complex|int|long|float|oct|hex|index|coerce|enter|exit)__((?=[^a-zA-Z0-9_\\.])|$)", syntaxengine.SyntElemFunc),
            ("((?<=[^a-zA-Z0-9_\\.])|^)(divmod|globals|print|repr|delattr|basestring|hash|dir|all|map|eval|compile|hex|setattr|abs|max|ord|next|help|execfile|any|reversed|reduce|super|sum|sorted|vars|slice|iter|input|reload|round|raw_input|id|callable|oct|ascii|staticmethod|isinstance|cmp|file|issubclass|locals|min|pow|getattr|hasattr|chr|__import__|classmethod|unichr|bool|open|filter|len|format|object|bin|exec|type|enumerate|property|zip)(?=\\s*\()", syntaxengine.SyntElemFunc),
            ("((?<=[^a-zA-Z0-9_\\.])|^)(del|from|while|as|elif|global|with|assert|else|if|pass|yield|break|except|import|print|class|exec|in|raise|continue|finally|return|def|for|try|__all__)($|(?=[^a-zA-Z0-9_\\.]))", syntaxengine.SyntElemKeyWord),
            ("((?<=[^a-zA-Z0-9_\\.])|^)(int|long|complex|float|str|unicode|bytes|bytearray|memoryview|tuple|list|set|frozenset|dict|range|xrange)($|(?=[^a-zA-Z0-9_\\.]))", syntaxengine.SyntElemType)
        ]
# }}}

# Javascript syntax tree {{{
class SyntTreeJS(syntaxengine.SyntTreeParser):
    class SyntTreeJSImport(syntaxengine.SyntTreeParser):
        RULE = [
                [
                    ("/\\*(.|\\s)*?\\*/", syntaxengine.SyntElemComment),
                    ("//.*?(?=\\n)", syntaxengine.SyntElemComment),
                    ("\"((\\\\\\\\|\\\\\")|[^\"])*\"", syntaxengine.SyntElemStr),
                    ("'((\\\\\\\\|\\\\')|[^'])*'", syntaxengine.SyntElemStr)
                ],
                ("(\\{|\\}|\\*|,|;)", syntaxengine.SyntElemSymbol),
                ("((?<=[^a-zA-Z0-9_\\.])|^)(import|as|from)($|(?=[^a-zA-Z0-9_\\.]))", syntaxengine.SyntElemKeyWord)
                ]
    RULE = [
            [
                ("/\\*(.|\\s)*?\\*/", syntaxengine.SyntElemComment),
                ("//.*?(?=\\n)", syntaxengine.SyntElemComment),
                ("\"((\\\\\\\\|\\\\\")|[^\"])*\"", syntaxengine.SyntElemStr),
                ("'((\\\\\\\\|\\\\')|[^'])*'", syntaxengine.SyntElemStr),
                ("/((\\\\\\\\|\\\\/)|[^/])*/", syntaxengine.SyntElemDSL),
                ("(^|(?<=[^a-zA-Z0-9_\\\\.]))(import(?=\\s|\\*|\\{|\"|\'))([^'\"/]|/[^*'\"]|(/\\*(.|\\s)*?\\*/|\"((\\\\\\\\|\\\\\")|[^\"])*\"|'((\\\\\\\\|\\\\')|[^'])*'|//.*?(?=\\n)))*?(;|\\n)",SyntTreeJSImport)
            ],
            ("(?<=[^a-zA-Z0-9_\\.])([0-9]+((\\.[0-9]*)?([eE][\+-]?[0-9]+)?)|\\.[0-9]+([eE][\+-]?[0-9]+)?|0x[0-9a-fA-F]+)($|(?=[^a-zA-Z0-9_\\.]))", syntaxengine.SyntElemValue),
            ("(?<=[^a-zA-Z0-9_\\.])true|true|null|NaN|Infinity($|(?=[^a-zA-Z0-9_\\.]))", syntaxengine.SyntElemValue),
            ("((?<=[^a-zA-Z0-9_\\.])|^)(var|let|const|function\\s*\\*|function|=>|yield\\s*\\*|yield|for|if|else|return|switch|case|throw|try|cache|finally|while|with|new|delete|class|get|set)($|(?=[^a-zA-Z0-9_\\.]))", syntaxengine.SyntElemKeyWord),
            ("(((?<=[^a-zA-Z0-9_\\.])(in|of|instanceof|typeof)(?=[^a-zA-Z0-9_\\.]))|\\{|\\}|\\[|\\]|\\(|\\)|\\+\\+|\\+|--|-|\\*\\*|\\*|/|%|>>>|>>|<<|>|<|>=|<=|!==|!=|===|==|=|\\|\\||&&|!|&|\\||~|\\^|\\?|:|,|\\.|;)", syntaxengine.SyntElemSymbol),
            ("((?<=[^a-zA-Z0-9_\\.])|^)(Number|String|Boolean|Symbol|Object|null|undefined|Function|Array|ArrayBuffer|Date|Error|RegExp|Promise|Generator|JSON)($|(?=[^a-zA-Z0-9_\\.]))", syntaxengine.SyntElemType),
            ("((?<=[^a-zA-Z0-9_\\.])|^)(this|super)($|(?=[^a-zA-Z0-9_]))", syntaxengine.SyntElemKeyWord),
            ("((?<=[^a-zA-Z0-9_\\.])|^)(decodeURI|encodeURI|decodeURIComponent|encodeURIComponent|escape|eval|isFinite|isNaN|parseFloat|parseInt|unescape|uneval)(?=\\s*\()", syntaxengine.SyntElemFunc)
        ]
# }}}

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
