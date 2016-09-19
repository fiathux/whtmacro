# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re
from whtmacro import syntaxengine as syngine

# RegExp template {{{

def regexShift(s):
    regex_symb = ["\\",".","^","$","*","+","?","{","}","[","]","(",")","|"]
    for rs in regex_symb:
        s = s.replace(rs,"\\"+rs)
    return s

# General rule template
def mkruleTempGeneral(first_parse=""):
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
                            first_parse, head_parse, "(", wordexpr, ")", tail_parse, last_parse
                            ]),element
                    return curryFinal
                return curryLayer4
            return curryLayer3
        return curryLayer2
    return curryLayer1

# Word template partital functions
mkrulePartLeftWord = mkruleTempGeneral("((?<=[^a-zA-Z0-9_\.])|^)")("(?=[^a-zA-Z0-9_\.])")
mkrulePartRightWord = mkruleTempGeneral("(?<=[^a-zA-Z0-9_\.])")("($|(?=[^a-zA-Z0-9_\.]))")
mkrulePartUniqueWord = mkruleTempGeneral("((?<=[^a-zA-Z0-9_\.])|^)")("($|(?=[^a-zA-Z0-9_\.]))")
mkrulePartClassWord = mkruleTempGeneral("((?<=[^a-zA-Z0-9_\.])|^)")("($|(?=[^a-zA-Z0-9_]))")
# Expression template partital functions
mkrulePartLeftExp = mkruleTempGeneral("((?<=[^a-zA-Z0-9_])|^)")("(?=[^a-zA-Z0-9_\.])")
mkrulePartRightExp = mkruleTempGeneral("(?<=[^a-zA-Z0-9_\.])")("($|(?=[^a-zA-Z0-9_]))")
mkrulePartGeneralExp = mkruleTempGeneral("((?<=[^a-zA-Z0-9_])|^)")("($|(?=[^a-zA-Z0-9_]))")
mkrulePartUniqueExp = mkruleTempGeneral("(?<=[^a-zA-Z0-9_\.])")("(?=[^a-zA-Z0-9_\.])")

# General element rule
mkruleKeyword = mkrulePartUniqueWord()()(syngine.SyntElemKeyWord)
mkruleSimpType = mkrulePartUniqueWord()()(syngine.SyntElemType)
mkruleClassType = mkrulePartClassWord()()(syngine.SyntElemType)
mkruleFunc = mkruleTempGeneral(
        "((?<=[^a-zA-Z0-9_\.])|^)")("(?=\\s*\()")()()(syngine.SyntElemFunc)
mkruleSymbol = mkruleTempGeneral()()()()(syngine.SyntElemSymbol)

# }}}

# C syntax tree {{{
# support
class SyntCCommon(object):
    CSTY_COMMENT = ("/\\*(.|\\s)*?\\*/", syngine.SyntElemComment)
    CSTY_COMMENT_LINE = ("//.*?((?=\\n)|$)", syngine.SyntElemComment)
    CSTY_STR = ("\"((\\\\\\\\|\\\\\")|[^\"])*\"", syngine.SyntElemStr)
    CSTY_CHAR = ("'((\\\\\\\\|\\\\')|[^'])*'", syngine.SyntElemStr)
    C_NUM = (
            "[0-9]+((\\.[0-9]*)?([eE][\+-]?[0-9]+)?)", # integer or float
            "\\.[0-9]+([eE][\+-]?[0-9]+)?", # simple float
            "0x[0-9a-fA-F]+"    # hex
            )
    C_SPECVAL = ("true", "false", "NULL")
    CSTY_NUM = mkrulePartUniqueWord()()(syngine.SyntElemValue)(*C_NUM, re_shift=False)
    CSTY_SPECVAL = mkrulePartUniqueWord()()(syngine.SyntElemValue)(*C_SPECVAL)
# Tree
class SyntTreeC(syngine.SyntTreeParser):
    # Pre-process DSL {{{
    # Macro area
    class SyntTreeCMacro(syngine.SyntTreeParser):
        RULE = [
                ("^\\s+",syngine.SyntElem),
                ("^#[a-zA-Z]+",syngine.SyntElemKeyWord),
                [
                    SyntCCommon.CSTY_COMMENT,
                    SyntCCommon.CSTY_COMMENT_LINE,
                    SyntCCommon.CSTY_STR,
                    SyntCCommon.CSTY_CHAR
                ],
                SyntCCommon.CSTY_NUM,
                SyntCCommon.CSTY_SPECVAL
            ]
        def __str__(me):
            return "".join((
                "<span class=\"",syngine.SYNSTY["dsl"],"\">",
                super(SyntTreeC.SyntTreeCMacro,me).__str__(),
                "</span>"
                ))
    # Include area
    class SyntTreeCInclude(syngine.SyntTreeParser):
        RULE = [
                ("^\\s+",syngine.SyntElem),
                ("^#include",syngine.SyntElemKeyWord),
                [
                    SyntCCommon.CSTY_COMMENT,
                    SyntCCommon.CSTY_COMMENT_LINE,
                    ("(<[^\>]*>|\"((\\\\\\\\|\\\\\")|[^\"])*\")",syngine.SyntElemStr)
                ]
            ]
    #}}}
    # Word and element
    C_PREPROC = (
            "define", "undef", "if", "ifdef", "ifndef", "else", "endif", "error",
            "warning", "pragma"
            )
    
    C_TYPE = (
            "char", "short", "int", "unsigned", "long", "float", "double", "struct",
            "union", "void", "enum", "signed", "_Bool", "_Complex", "_Imaginary",
            "bool", "complex", "imaginary", "_Thread_local", "_Noreturn", "static",
            "extern", "inline", "restrict", "const", "volatile", "auto", "register",
            "_Atomic", "_Alignas"
            )
    C_KW = (
            "typedef", "break", "case", "continue", "default", "do", "else", "for",
            "goto", "if", "return", "switch", "while", "_Generic", "_Static_assert",
            "sizeof", "_Alignof", "alignof"
            )
    C_SYMBOL = (
            ".","->","++","--","+=","-=","*=","/=","%=","&=","|=","^=","<<=",">>=",
            "+","-","*","/","%","==","!=","<<",">>","<=",">=","<",">","=","?",":",
            "!","&&","||","~","&","|","^","(",")","[","]",",","{","}"
            )
    # pre-build
    CStyMacroTemp = lambda pre_rule: mkruleTempGeneral(pre_rule)(
            "(( |\\t)+(\\\\\\n|/\\*(.|\\s)*?\\*/|[^\\n])+|(\\s*)((?=\\n)|(?=/\\*)|(?=//)))")()()
    CStyMacroGen = CStyMacroTemp("(?<=\\n)( |\\t)*#") # General parser
    CStyMacroOnce = CStyMacroTemp("^( |\\t)*#") # First parser
    # Rule
    RULE = [
            [
                CStyMacroOnce(SyntTreeCInclude)("include"),
                CStyMacroOnce(SyntTreeCMacro)(*C_PREPROC)
            ],
            [
                SyntCCommon.CSTY_COMMENT,
                SyntCCommon.CSTY_COMMENT_LINE,
                SyntCCommon.CSTY_STR,
                SyntCCommon.CSTY_CHAR,
                CStyMacroGen(SyntTreeCInclude)("include"),
                CStyMacroGen(SyntTreeCMacro)(*C_PREPROC)
            ],
            SyntCCommon.CSTY_NUM,
            SyntCCommon.CSTY_SPECVAL,
            mkruleSimpType(*C_TYPE),
            mkruleKeyword(*C_KW),
            mkruleSymbol(*C_SYMBOL)
        ]
#}}}

# Golang syntax tree {{{
class SyntTreeGolang(syngine.SyntTreeParser):
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
    GOStyleType = mkrulePartRightWord()()(syngine.SyntElemType)
    RULE = [
            [
                SyntCCommon.CSTY_COMMENT,
                SyntCCommon.CSTY_COMMENT_LINE,
                SyntCCommon.CSTY_STR,
                SyntCCommon.CSTY_CHAR
            ],
            mkrulePartUniqueWord()()(syngine.SyntElemValue)(*GOLANG_NUM,re_shift=False),
            mkrulePartUniqueWord()()(syngine.SyntElemValue)(*GOLANG_SPECVAL),
            mkruleSymbol(*GOLANG_SYMBOL),
            mkruleKeyword(*GOLANG_KW),
            GOStyleType(*GOLANG_TYPE)
        ]
#}}}

# Python syntax tree {{{
class SyntTreePython(syngine.SyntTreeParser):
    # Range rule
    PYSTY_STR_DQ = ("[rbu]?\"((\\\\\\\\|\\\\\")|[^\"])*\"", syngine.SyntElemStr)
    PYSTY_STR_SQ = ("[rbu]?'((\\\\\\\\|\\\\')|[^'])*'", syngine.SyntElemStr)
    PYSTY_STR_DQML = (
            "[rbu]?\"{3}(\"{1,2}[^\"])?((\\\\\\\\|\\\\\"|[^\"]\"{1,2}[^\"])|[^\"])*\"{3}",
            syngine.SyntElemStr
            )
    PYSTY_STR_SQML = (
            "[rbu]?'{3}('{1,2}[^'])?((\\\\\\\\|\\\\'|[^']'{1,2}[^'])|[^'])*'{3}",
            syngine.SyntElemStr
            )
    PYSTY_COMMENT = ("#.*?(?=\\n)", syngine.SyntElemComment)
    # Word and element
    PYTH_NUM = (
            "[0-9]+((\\.[0-9]*)?([eE][\+-]?[0-9]+)?j?)",  # integer or normal float with complex
            "\\.[0-9]+([eE][\+-]?[0-9]+)?j?", # simple float with complex
            "0x[0-9a-fA-F]+" # hex integer
            )
    PYTH_SPECVAL = ("True", "False", "None")
    PYTH_SYMBOL_REG = ("lambda","not +in","is +not","and","not","or","in","is")
    PYTH_SYMBOL = (
            "==", "!=", "<<", ">>", ">", "<", ">=", "<=", "=", ",", "(", ")",
            "[", "]", "{", "}", "//", "**", "|", "^", "&", "+", "-", "*", "/",
            "%", "~", ":", "."
            )
    PYTH_FUNC_SEPC = (
            "new", "init", "del", "repr", "str", "lt", "le", "eq", "ne", "gt",
            "ge", "cmp", "rcmp", "hash", "nonzero", "unicode", "getattr", "setattr",
            "delattr", "getattribute", "get", "set", "delete", "metaclass",
            "instancecheck", "subclasscheck", "call", "len", "getitem", "missing",
            "setitem", "delitem", "iter", "reversed", "contains", "getslice",
            "setslice", "delslice", "add", "sub", "mul", "floordiv", "mod", "divmod",
            "pow", "lshift", "rshift", "and", "xor", "or", "div", "truediv", "radd",
            "rsub", "rmul", "rdiv", "rtruediv", "rfloordiv", "rmod", "rdivmod",
            "rpow", "rlshift", "rrshift", "rand", "rxor", "ror", "iadd", "isub",
            "imul", "idiv", "itruediv", "ifloordiv", "imod", "ipow", "ilshift",
            "irshift", "iand", "ixor", "ior", "neg", "pos", "abs", "invert", "complex",
            "int", "long", "float", "oct", "hex", "index", "coerce", "enter", "exit"
            )
    PYTH_FUNC = (
            "divmod", "globals", "print", "repr", "delattr", "basestring", "hash",
            "dir", "all", "map", "eval", "compile", "hex", "setattr", "abs", "max",
            "ord", "next", "help", "execfile", "any", "reversed", "reduce", "super",
            "sum", "sorted", "vars", "slice", "iter", "input", "reload", "round",
            "raw_input", "id", "callable", "oct", "ascii", "staticmethod",
            "isinstance", "cmp", "file", "issubclass", "locals", "min", "pow",
            "getattr", "hasattr", "chr", "__import__", "classmethod", "unichr",
            "bool", "open", "filter", "len", "format", "object", "bin", "exec",
            "type", "enumerate", "property", "zip"
            )
    PYTH_KW = (
            "del", "from", "while", "as", "elif", "global", "with", "assert", "else",
            "if", "pass", "yield", "break", "except", "import", "print", "class",
            "exec", "in", "raise", "continue", "finally", "return", "def", "for",
            "try", "__all__", "__slots__"
            )
    PYTH_TYPE = (
            "int", "long", "complex", "float", "str", "unicode", "bytes", "bytearray",
            "memoryview", "tuple", "list", "set", "frozenset", "dict", "range",
            "xrange"
            )
    # Pre-bulid
    PYTH_SYB_REGC = "(" + mkrulePartUniqueExp()()(None)(*PYTH_SYMBOL_REG, re_shift=False)[0] + ")"
    PyStySpecFunc = mkruleTempGeneral("(?<=\\s|\\.)")("(?=\\s*\()")("__")("__")
    # Rule
    RULE = [
            [
                PYSTY_STR_DQML,
                PYSTY_STR_SQML,
                PYSTY_COMMENT,
                PYSTY_STR_DQ,
                PYSTY_STR_SQ
            ],
            mkrulePartUniqueWord()()(syngine.SyntElemValue)(*PYTH_NUM,re_shift=False),
            mkrulePartUniqueWord()()(syngine.SyntElemValue)(*PYTH_SPECVAL),
            PyStySpecFunc(syngine.SyntElemFunc)(*PYTH_FUNC_SEPC),
            mkruleFunc(*PYTH_FUNC),
            mkruleClassType(*PYTH_TYPE),
            mkruleTempGeneral()()()()(syngine.SyntElemSymbol)(
                *PYTH_SYMBOL, pre_rule=PYTH_SYB_REGC),
            mkruleKeyword(*PYTH_KW)
        ]
# }}}

# Javascript syntax tree {{{
class SyntTreeJS(syngine.SyntTreeParser):
    # Import sub-statment
    class SyntTreeJSImport(syngine.SyntTreeParser):
        RULE = [
                [
                    SyntCCommon.CSTY_COMMENT,
                    SyntCCommon.CSTY_COMMENT_LINE,
                    SyntCCommon.CSTY_STR,
                    SyntCCommon.CSTY_CHAR
                ],
                mkruleSymbol("{", "}", "*", ",", ";"),
                mkruleKeyword("import", "as", "from")
            ]
    # Range rule
    JSSTY_REGEXP = ("/((\\\\\\\\|\\\\/)|[^/])*/", syngine.SyntElemDSL)
    JSSTY_IMPORT = (
            "".join(("(^|(?<=[^a-zA-Z0-9_\\\\.]))",
            "(import(?=\\s|\\*|\\{|\"|\'))",
            "(", "|".join((
                "[^'\"/]", # general content (no string & no comment)
                "/[^*'\"/]", # case general content follow "/"
                "(/\\*(.|\\s)*?\\*/", # comment range
                "\"((\\\\\\\\|\\\\\")|[^\"])*\"", # double-quote string
                "'((\\\\\\\\|\\\\')|[^'])*'", # single-quote string
                "//.*?(?=\\n))" # comment line
                )),
            ")",
            "*?(;|\\n)")), SyntTreeJSImport)
    # Word and element
    JS_NUM = SyntCCommon.C_NUM
    JS_SPECVAL = ("true", "true", "null", "NaN", "Infinity")
    JS_KW_NEW = ("function\\s*\\*", "yield\\s*\\*")
    JS_KW = (
            "=>", "var", "let", "const", "function", "yield", "for", "if", "else",
            "return", "switch", "case", "throw", "try", "cache", "finally", "while",
            "with", "new", "delete", "class", "get", "set"
            )
    JS_KW_EXP = ("this", "super")
    JS_SYMBOL_REG = ("in", "of", "instanceof", "typeof")
    JS_SYMBOL = (
            "{", "}", "[", "]", "(", ")", "++", "+", "--", "-", "**", "*", "/", "%",
            ">>>", ">>", "<<", ">", "<", ">=", "<=", "!==", "!=", "===", "==", "=",
            "||", "&&", "!", "&", "|", "~", "^", "?", ":", ",", ".", ";"
            )
    JS_FUNC = (
            "decodeURI", "encodeURI", "decodeURIComponent", "encodeURIComponent",
            "escape", "eval", "isFinite", "isNaN", "parseFloat", "parseInt",
            "unescape", "uneval"
            )
    JS_TYPE = (
            "Number", "String", "Boolean", "Symbol", "Object", "null", "undefined",
            "Function", "Array", "ArrayBuffer", "Date", "Error", "RegExp", "Promise",
            "Generator", "JSON"
            )
    # Pre-bulid
    JS_SYB_REGC = "(" + mkrulePartUniqueExp()()(None)(*JS_SYMBOL_REG)[0] + ")"
    JS_KW_NEWC = "|".join(JS_KW_NEW)
    JSStyleClassKeyword = mkrulePartClassWord()()(syngine.SyntElemKeyWord)
    # Rule
    RULE = [
            [
                SyntCCommon.CSTY_COMMENT,
                SyntCCommon.CSTY_COMMENT_LINE,
                SyntCCommon.CSTY_STR,
                SyntCCommon.CSTY_CHAR,
                JSSTY_REGEXP,
                JSSTY_IMPORT
            ],
            mkrulePartUniqueWord()()(syngine.SyntElemValue)(*JS_NUM,re_shift=False),
            mkrulePartUniqueWord()()(syngine.SyntElemValue)(*JS_SPECVAL),
            mkruleFunc(*JS_FUNC),
            mkruleClassType(*JS_TYPE),
            JSStyleClassKeyword(*JS_KW_EXP),
            mkruleKeyword(*JS_KW, pre_rule=JS_KW_NEWC),
            mkruleTempGeneral()()()()(syngine.SyntElemSymbol)(
                *JS_SYMBOL, pre_rule=JS_SYB_REGC)
        ]
# }}}

# golang syntax
@syngine.decoRegSyntax("golang")
def synt_golang(langStr):
    return "".join(("<pre class=\"lang-go\">","%s" % SyntTreeGolang(langStr),"</pre>"))

# python syntax
@syngine.decoRegSyntax("python")
def synt_python(langStr):
    return "".join(("<pre class=\"lang-py\">","%s" % SyntTreePython(langStr),"</pre>"))

# python syntax
@syngine.decoRegSyntax("javascript")
def synt_javascript(langStr):
    return "".join(("<pre class=\"lang-js\">","%s" % SyntTreeJS(langStr),"</pre>"))

# C syntax
@syngine.decoRegSyntax("c")
def synt_c11(langStr):
    return "".join(("<pre class=\"lang-c\">","%s" % SyntTreeC(langStr),"</pre>"))
