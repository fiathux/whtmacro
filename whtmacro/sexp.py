# -*- coding: utf-8 -*-

'''
Wonderland HTML file template
S-Expression module
------------------------------
Fiathu Su(fiathux@gmail.com)
2015-2017
'''

from __future__ import unicode_literals

import re

# module exception prototype
class excSExp(Exception):pass

# S-Expression element prototype{{{
class SElement(object):
    # the members "type", "line" and "column" must defined in every implement
    def __init__(me):
        me.type = "element"
        me.line = None
        me.column = None

    # the call method return a result of expression
    def  __call__(me):
        return None
#}}}

# S-Expression element class{{{
class SValue(SElement):
    # data-type parser
    PARSE_INT = re.compile("^([\\+\\-])?([1-9][0-9]*|0)$")
    PARSE_NUM = re.compile("^(([\\+\\-])?((([1-9][0-9]*|0)\\.[0-9]*|\\.[0-9]+|[1-9][0-9]*|0)([eE](\\+|-)?[0-9]+)?))(([\\+\\-]((([1-9][0-9]*|0)\\.[0-9]*|\\.[0-9]+|[1-9][0-9]*|0)([eE](\\+|-)?[0-9]+)?))?(i))?$")
    PARSE_OCT = re.compile("^(0o|0)([0-7]+)$")
    PARSE_HEX = re.compile("^0x[0-9a-fA-F]+$")
    PARSE_SPECFLOAT = re.compile("^([\\+\\-])?(Inf|NaN)$")
    PARSE_BOOL = re.compile("^(TRUE|FALSE)$")
    PARSE_NONE = re.compile("^Nil$")
    PARSE_SHIFTSTR = re.compile("^\\[\\[(?P<quote>-{,5})\\[(.*)\\](?P=quote)\\]\\]$",re.S)

    def __init__(me, val, ln = 0, cn = 0):
        me.value, me.type = me.type_int(val) or me.type_numeric(val) or me.type_bool(val) or\
                me.type_none(val) or me.type_string(val)
        me.expression = val
        me.line = ln
        me.column = cn

    def __call__(me):
        return me.value

    # parse convert integer
    @classmethod
    def type_int(c, val):
        def convint(v):
            mch = c.PARSE_INT.match(v)
            return mch and (eval(v), "int")
        def convoct(v):
            mch = c.PARSE_OCT.match(v)
            return mch and ( eval(v) if mch.group(1) == "0o" else eval("0o" + mch.group(2)), "int")
        def convhex(v):
            mch = c.PARSE_HEX.match(v)
            return mch and (eval(v), "int")
        return convint(val) or convoct(val) or convhex(val)

    # parse convert numeric
    @classmethod
    def type_numeric(c,val):
        def convnumeric(v):
            mch = c.PARSE_NUM.match(v)
            return mch and ( eval("%s%s%s" % (
                mch.group(1) or "",
                mch.group(9) or "",
                ((mch.group(15) and "j") or "")
                ) ), "numeric")
        def convspecial(v):
            mch = c.PARSE_SPECFLOAT.match(v)
            return mch and (float(mch.group(2)) * ((mch.group(1) == "-" and -1) or 1), "numeric")
        return convnumeric(val) or convspecial(val)

    # parse convert none
    @classmethod
    def type_none(c,val):
        return c.PARSE_NONE.match(val) and (None, "none")

    # parse convert boolean
    @classmethod
    def type_bool(c,val):
        return c.PARSE_BOOL.match(val) and (val == "TRUE", "bool")

    # parse convert string
    @classmethod
    def type_string(c,val):
        def escapechar(s):
            return "\\".join(
                    map(lambda ss: re.sub("\\\\([ \\(\\)'\"])","\g<1>",ss).replace(
                        "\\n","\n").replace("\\t","\t"),
                    s.split("\\\\"))
                    )
        def convquote(v):
            mch = v and (v[0] == v[-1]) and (v[0] == "'" or v[0] == '"') and len(v) > 1
            return mch and (escapechar(v[1:-1]), "string")
        def convshiftstr(v):
            mch = c.PARSE_SHIFTSTR.match(v)
            return mch and (mch.group(2), "string")
        def fullstr(v):
            return (escapechar((v and v) or ""), "string")
        return convquote(val) or convshiftstr(val) or fullstr(val)
#}}}

# S-Expression function prototype{{{
class SExpression(SElement):
    def __init__(me, exp_gen, env, ln = 0, cn = 0):
        me.type = "expression"
        me.env = SScope(env)
        me.line = ln
        me.column = cn
        # value list must defined in s-function
        me._Lisp = [itm for itm in exp_gen(me.env)]

    @classmethod
    def call(c,name,param):
        return [name] + ([p() for p in param] if param else [])

    def __call__(me):
        return me.call(me._Lisp[0], (exp() for exp in me._Lisp[1:]))
#}}}

# basic data environment scope class {{{
class SScope(dict):
    def __init__(me,parent = None):
        def keyerror(k):
            raise KeyError(k)
        # scope chain oprations
        me.backward = lambda : parent # backward scope
        if parent:
            me.setGlb = lambda k,v: parent.setGlb(k,v)  # set value to root
            me.getGlb = lambda k: parent.getGlb(k)      # get value from root
            me.delGlb = lambda k: parent.delGlb(k)      # delete value from root
            me.inGlb = lambda k: parent.inGlb(k)        # check value in root
            me.getPar = lambda k: parent[k]             # get value from parent
            me.inPar = lambda k: k in parent            # check value in parent
        else: # root scope
            me.setGlb = lambda k,v: me.__setitem__(k,v)
            me.getGlb = lambda k: me[k]
            me.delGlb = lambda k: me.__delitem__(k)
            me.inGlb = lambda k: me._contians(k)
            me.getPar = lambda k: keyerror(k)
            me.inPar = lambda k: False

    def __getitem__(me,key):
        return super(SScope,me).__getitem__(key) if me.contains(key) else me.getPar(key)

    def __contains__(me,key):
        return me.contains(key) or me.inPar(key)

    def contains(me,key):
        return super(SScope,me).__contains__(key)
#}}}

_MODULE_ENV = SScope()

# make default S-Expression Node factory
def mkModSFactroy(expClass = SExpression)
    def moduleSFactory(expiter, env):
        pass

EPARSE_GENERAL = re.compile("^(\\\\\\\\|\\\\\\s|\\S)+")
EPARSE_DQUOTE = re.compile("^\"(\\\\\\\\|\\\\\"|[^\"])*\"")
EPARSE_QUOTE = re.compile("^'(\\\\\\\\|\\\\'|[^'])*'")
EPARSE_SHIFTSTR = re.compile("^\\[\\[(?P<quote>-{,5})\\[(.*?)\\](?P=quote)\\]\\]",re.S)

# export S-Expression parser factroy
def SParseFactory(expFactory = mkModSFactroy()):
    def SParser(exp_str, ln = 0, cn = 0):
        def iterElem(s):
            stacks = [(ln,cn)]
            for i in range(0,len(s)):
                pass
        def export():
            return iterElem(s[1:-1])
        return export
    return SExpParser
