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
from collections import namedtuple
from whtmacro import searchTree

MAX_STACK_DEPTH = 200

# Support class{{{
# S-Context position class
class SPosition(namedtuple("SPosition",["line","column","start","end"])):
    def renew(me, line = None, column = None, start = None, end = None):
        return SPosition(
                me.line if line is None else line,
                me.column if column is None else column,
                me.start if start is None else start,
                me.end if end is None else end
                )

# module exception prototype
class excSExp(Exception):
    def __init__(me, pos, msg = ""):
        me.position = pos
        me.message = msg
    def __str__(me):
        return "s-expression error in position ln:%d, col:%d%s" % (
                me.position.line,
                me.position.column,
                " - %s" % me.message if me.message else "",
                )
#}}}

# S-Expression element prototype{{{
class SElement(object):
    # the members "type" and "position" must defined in every implement
    def __init__(me):
        me.type = "element"
        me.position = SPosition(0,0,0,0)

    # the call method return a result of expression
    def  __call__(me):
        return None
#}}}

# S-Expression value element class{{{
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

    def __init__(me, val, pos = SPosition(0,0,0,0), env = None):
        me.value, me.type = me.type_int(val) or me.type_numeric(val) or me.type_bool(val) or\
                me.type_none(val) or me.type_string(val)
        me.expression = val
        me.position = pos

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
                    map(lambda ss: re.sub("\\\\([ \\(\\)'\"\\[])","\g<1>",ss).replace(
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
    def __init__(me, exp_gen, env, pos = SPosition(0,0,0,0)):
        me.type = "expression"
        me.position = pos
        me.env = SScope(env, me)
        # value list must defined in s-function
        me._Lisp = [itm for itm in exp_gen(me.env)]
        if me._Lisp:
            me.closeExp(me._Lisp[-1].position.end)
        else:
            raise excSExp(pos,"invalid empty expression")

    # set end-point of exporession
    def closeExp(me,endpoint):
        me.position = me.position.renew(end = endpoint)

    @classmethod
    def call(c,name,param):
        return [name] + ([p for p in param] if param else [])

    def __call__(me):
        return me.call(me._Lisp[0](), (exp() for exp in me._Lisp[1:]))
#}}}

# basic data environment scope class {{{
class SScope(dict):
    def __init__(me,parent = None, owner = None):
        def keyerror(k):
            raise KeyError(k)
        # scope chain oprations
        me.backward = lambda : parent # backward scope
        me.owner = owner
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

# context parser regexp {{{
EPARSE_STRIP = re.compile("\S")
EPARSE_GENERAL = re.compile("(\\\\\\\\|\\\\\\s|\\\\\\(|\\\\\\)|[^\\s\\(\\)])+")
EPARSE_DQUOTE = re.compile("\"(\\\\\\\\|\\\\\"|[^\"])*\"")
EPARSE_QUOTE = re.compile("'(\\\\\\\\|\\\\'|[^'])*'")
EPARSE_SHIFTSTR = re.compile("\\[\\[(?P<quote>-{,5})\\[(.*?)\\](?P=quote)\\]\\]",re.S)
EPARSE_PACKSTART = re.compile("[\"']|\\[\\[-{,5}\\[")
#}}}

# export S-Expression parser factroy {{{
# expression factory prototype: factory(exp_iter, env, position)
# values factory prototype: factory(exp_str, position, env)
def SParseFactory(expFactory = SExpression, valFactory = SValue):
    # expression parser
    def SParser(exp_str, initenv = _MODULE_ENV, start = 0, ln = 0, cn = 0):
        lnIndex = searchTree.SearchRBTree(lambda a,b: 1 if a[0]>b[1] else (-1 if a[1]<b[0] else 0))
        # support{{{
        # normalize text line information
        def linelize(exp, orig_ln, org_cn):
            def getPosFunc(linenum,linekey):
                return (linekey ,
                        lambda idx: (linenum + orig_ln ,
                            idx - linekey[0] + (0 if linenum else org_cn)))
            lnfind = re.compile("\n")
            lnnum = 0
            lnstart = 0
            for lnpos in lnfind.finditer(exp):
                yield getPosFunc(lnnum, (lnstart, lnpos.start()))
                lnnum = lnnum + 1
                lnstart = lnpos.end()
            if lnstart < len(exp):
                yield getPosFunc(lnnum, (lnstart, len(exp)))
        # convert string index to position object
        def index2position(index,end = None):
            lninf = lnIndex.find((index,index))(index)
            return SPosition(lninf[0], lninf[1], index, end if end else index)
        #}}}
        # make line serial
        exp_str = exp_str.replace("\r\n","\n").replace("\r","\n")
        for lkey,lproc in linelize(exp_str, ln, cn): lnIndex.add(lkey,lproc)
        stack_depth = [] # syntax stack
        # element build{{{
        # create expression element
        def enterExpStack(s, index, env):
            pos = index2position(index)
            if len(stack_depth) > MAX_STACK_DEPTH:
                raise excSExp(pos, "Stack depth overflow")
            itrLmd = lambda exenv: iterElem(s, index + 1, exenv)
            stack_depth.append(pos) # push syntax stack
            try:
                rst = expFactory(itrLmd, env, pos)
                endidx = rst.position.end
                if len(s) >= endidx:
                    mch = EPARSE_STRIP.search(s,endidx)
                    if mch and s[mch.start()] == ")":
                        rst.closeExp(mch.start() + 1)
                        return rst
                raise excSExp(pos, "Incomplete expression")
            finally:
                stack_depth.pop() # pop syntax stack
        # create value element
        def oneElement(s, index, env):
            if EPARSE_PACKSTART.match(s,index):
                exp_ang = EPARSE_SHIFTSTR.match(s,index) or EPARSE_QUOTE.match(s,index) or \
                        EPARSE_DQUOTE.match(s,index)
                if not exp_ang:
                    raise excSExp(index2position(index), "Unexcepted end of string")
            else:
                exp_ang = EPARSE_GENERAL.match(s,index)
            pos = index2position(index, exp_ang.end())
            return valFactory(s[index:exp_ang.end()], pos, env)
        #}}}
        # element iterator
        def iterElem(s, index, env, atroot = False):
            while index < len(s):
                start_point = EPARSE_STRIP.search(s, index)
                if not start_point: return
                if s[start_point.start()] == ")":
                    if not atroot: # close expression
                        return
                    else: # Unexpected close
                        raise excSExp(index2position(start_point.start()),
                            "Unexpected praentthese")
                rst = (enterExpStack if s[start_point.start()] == "(" else oneElement)(
                        s, start_point.start(), env)
                yield rst
                index = rst.position.end
        # export parser
        def export():
            return iterElem(exp_str, start, initenv, True)
        return export
    return SParser
#}}}
