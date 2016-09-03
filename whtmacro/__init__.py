# -*- coding: utf-8 -*-

'''
Wonderland HTML file template
Initialize module
------------------------------
Fiathu Su(fiathux@gmail.com)
2015-2016
'''
from __future__ import print_function
from __future__ import unicode_literals

import sys
import os
import os.path
import re
import json
import time
from collections import namedtuple
from whtmacro.searchTree import SearchRBTree

OPTLIST = {}
ENV = {}

MAX_IMPORT_DEPTH = 20

# Add default extension path in current work-directory
def setDefaultExtPath():
    if os.name == "nt": pSplit = "\\"
    else: pSplit = "/"
    workdir = os.getcwd()
    if workdir[-1] != pSplit:
        workdir = workdir + pSplit
    sys.path.append(workdir + "whtmacro-ext")
setDefaultExtPath()

# Print help text
def help():
    print("whtmacro filelist...")

# Position of command in document
class DocPosition(namedtuple("DocPosition",["file","ln","col"])):
    __slots__ = ()
    def __str__(me):
        return "file: \"%s\" - line: %d - col: %d" % me

# Exceptions {{{
class ExcWHTBase(Exception):
    @staticmethod
    def doc_pos():
        return ENV["docpos"]

class ExcFileError(ExcWHTBase):
    def __init__(me,fname):
        me.message = "Invalid file name \"%s\"" % (fname)
        if "docpos" in ENV:
            me.message = me.message + (" in %s" % (me.doc_pos(),))

class ExcCMDError(ExcWHTBase):
    def __init__(me,cmd):
        me.message = "Unknown command [%s] in %s" % (cmd,me.doc_pos())

class ExcCMDParam(ExcWHTBase):
    def __init__(me):
        me.message = "Paramete error in %s" % (me.doc_pos(),)

class ExcCMDVerbFound(ExcWHTBase):
    def __init__(me,vname):
        me.message = "Undefined variable name [%s] in %s" % (vname,me.doc_pos())

class ExcModName(ExcWHTBase):
    def __init__(me,mname):
        me.message = "Invaild module name [%s] in %s" % (mname,me.doc_pos())

class ExcModImp(ExcWHTBase):
    def __init__(me,mname):
        me.message = "Can not import module [%s] in %s" % (mname,me.doc_pos())

class ExcImportDepthError(ExcWHTBase):
    def __init__(me):
        me.message = "Too many import depth:\n    %s" % ("\n    ".join(ENV["import_deep"]),)
#}}}

# Read files iterator
def iterFile(fli):
    for f in fli:
        if not os.path.isfile(f):
            raise ExcFileError(f)
        yield open(f,"rb").read().decode("utf-8").replace("\r\n","\n").replace("\r","\n"),f

# Build-in plugins{{{

# Opt-plugins decorate
def decoOptPart(name):
    def realDeco(func):
        OPTLIST[name] = func
        return func
    return realDeco

#Plugin: import wh scripts
@decoOptPart("import")
def opt_include(param):
    return processfiles(param)

#Plugin: include files
def create_include():
    @decoOptPart("include*")
    def opt_include_origi(param):
        return "".join(map(lambda a:a[0],iterFile(param))).strip()
    @decoOptPart("include")
    def opt_include_html(param):
        return "".join(map(lambda s:"\n".join([line.strip() for line in s[0].split("\n")]), iterFile(param))).strip()
#Execute create
create_include()

#Plugin: import module
@decoOptPart("module")
def opt_maodule(param):
    parseMName = re.compile("^[_a-zA-Z][_a-zA-Z0-9]*(\.[_a-zA-Z][_a-zA-Z0-9]*)*$").match
    loadstr = []
    #Import module list
    def imp_modules(mlist):
        for m in mlist:
            if not parseMName(m):
                raise ExcModName(m)
            try:
                mget = __import__(m,None,None,["wht_entry"])
            except:
                raise ExcModImp(m)
            if hasattr(mget,"wht_entry"):
                loadstr.append(mget.wht_entry())
        return "".join(loadstr)
    return imp_modules(param)

#Plugin: variable set
@decoOptPart("set")
def opt_set(param):
    if len(param) != 2 or not param[0]:
        raise ExcCMDParam()
    if "varb" not in ENV:
        ENV["varb"]={param[0]:param[1]}
    else:
        ENV["varb"][param[0]]=str(param[1])
    return ""

#Plugin: variable get
@decoOptPart("get")
def opt_get(param):
    if len(param) != 1 or not param[0]:
        raise ExcCMDParam()
    if "varb" not in ENV or param[0] not in ENV["varb"]:
        raise ExcCMDVerbFound(param[0])
    return ENV["varb"][param[0]]

#Plugin: output formated datetime
@decoOptPart("date")
def opt_date(param):
    persetFmt = {
            "+":"%Y-%m-%d %H:%M:%S %Z",
            "simple":"%Y-%m-%d",
            "simple+":"%Y-%m-%d %H:%M:%S %Z",
            "chinese":"%Y年%m月%d日",
            "chinese+":"%Y年%m月%d日 %H时%M分%S秒 %Z",
            "english":"%a, %b %m %Y",
            "english+":"%a, %b %m %Y %H:%M:%S %Z"
            }
    if len(param) < 1 or param[0] not in persetFmt: fmt = persetFmt["simple"]
    else: fmt = persetFmt[param[0]]
    if len(param) >= 2 and param[1] == "gmt":
        time_src = time.gmtime
        fmt = "%%".join(map(lambda a: re.sub("%Z","GMT",a),fmt.split("%%")))
    else: time_src = time.localtime
    if type(fmt).__name__ == "unicode": #for python2
        fmt=fmt.encode("utf-8")
        return time.strftime(fmt,time_src()).decode("utf-8")
    else:#for python3
        return time.strftime(fmt,time_src())

#}}}

#Import process
def processfiles(filelist):
    PARSETAG = re.compile("<\((\"((\\\\\\\\|\\\\\")|[^\"])*\"(\s*,\s*(\"((\\\\\\\\|\\\\\")|[^\"])*\"|[0-9]+(.[0-9]+)*))*)\)>").finditer
    #Scan lines position and make index {{{
    def iterLineLen(lineStr): 
        pos = 0
        for lnindex in range(0,len(lineStr)):
            linelen = len(lineStr[lnindex])
            #( key: (range_start, range_end), value: (line_num, range_start, len) )
            yield ((pos,pos+linelen),(lnindex,pos,linelen))
            pos = pos + linelen + 1
    def scanLine(lineStr):
        #Order-tree index
        lnSearch = SearchRBTree(lambda a,b:
                0 if ((a[0]>=b[0] and a[1]<=b[1]) or
                    (b[0]>=a[0] and b[1]<=a[1])) else 1 if a[0]>b[0] else -1
                )
        for lineRange,lnInfo in iterLineLen(lineStr):
            lnSearch.add(lineRange,lnInfo)
        return lnSearch
    #}}}

    #Parse file element
    def iterFileSlice(fli):
        for fdataStr,f in iterFile(fli):
            fdata = fdataStr.split("\n")
            start = 0
            schline = scanLine(fdata) # make line-number index
            fdata = "\n".join(fdata)
            pnode = PARSETAG(fdata)
            for pone in pnode:
                pickdata = fdata[start:pone.start()]
                start = pone.end()
                parse = json.loads("["+pone.group(1)+"]")
                yield pickdata
                yield (parse,pone,f,schline.find((pone.start(),pone.start())))
            yield fdata[start:]
    #Parse opt-plugins
    def iterDoParse():
        for ele in iterFileSlice(filelist):
            if type(ele).__name__ == "unicode" or type(ele) == str: # python2 for "unicode" and python3 for "str"
                yield(ele)
            else:
                ENV["docpos"] = DocPosition(ele[2], ele[3][0] + 1, ele[1].start() - ele[3][1] + 1)
                if ele[0][0] not in OPTLIST:
                    raise ExcCMDError(ele[0][0])
                yield OPTLIST[ele[0][0]](ele[0][1:])
    try:
        if "import_deep" not in ENV:    #Process import stack
            ENV["import_deep"] = [",".join(filelist)]
        else:
            ENV["import_deep"].append("%s - in %s" % (",".join(filelist),ENV["docpos"]))
        if len(ENV["import_deep"]) > MAX_IMPORT_DEPTH:
            raise ExcImportDepthError()
        return "\n".join(filter(lambda a:a,map(lambda a:a.strip(), "".join(iterDoParse()).split("\n")))) #Begin parse
    finally:
        ENV["import_deep"].pop()

def main():
    #Entry
    args = sys.argv[1:]
    if not args or args[0] in {"-h","--help"}:
        help()
    else:
        try:
            outbuff = processfiles(args)
            if type(outbuff).__name__ == "unicode": # for python2
                sys.stdout.write(outbuff.encode("utf-8"))
            else: # for python3
                sys.stdout.write(outbuff)
        except ExcWHTBase as e:
            print("error - " + e.message, file=sys.stderr)
