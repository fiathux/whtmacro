# -*- coding: utf-8 -*-

'''
Wonderland HTML file template
Initialize module
------------------------------
Fiathu Su(fiathux@gmail.com)
2015-2016
'''
from __future__ import print_function

import sys
import os.path
import re
import json
from whtmacro.searchTree import SearchRBTree

OPTLIST = {}
ENV = {}

# Print help text
def help():
    print("whtmacro filelist...")

#Exceptions {{{
class ExcFileError(Exception):
    def __init__(me,fname):
        me.message = "Invalid file name: " + fname

class ExcCMDError(Exception):
    def __init__(me,fname,cmd,pos):
        me.message = "Unknown command [%s] in file \"%s\" pos ln:%d - col:%d" % (cmd,fname,pos[0],pos[1])

class ExcCMDParam(Exception):
    def __init__(me,fname,pos):
        me.message = "Paramete error in file \"%s\" pos ln:%d - col:%d" % (fname,pos[0],pos[1])

class ExcCMDVerbFound(Exception):
    def __init__(me,fname,pos,vname):
        me.message = "Undefined variable name [%s] in file \"%s\" pos ln:%d - col:%d" % (vname,fname,pos[0],pos[1])

class ExcModName(Exception):
    def __init__(me,mname,fname,pos):
        me.message = "Invaild module name [%s] in file \"%s\" pos ln:%d - col:%d" % (mname,fname,pos[0],pos[1])

class ExcModImp(Exception):
    def __init__(me,mname,fname,pos):
        me.message = "Can not import module [%s] in file \"%s\" pos ln:%d - col:%d" % (mname,fname,pos[0],pos[1])
#}}}

# Opt-plugins decorate
def decoOptPart(name):
    def realDeco(func):
        OPTLIST[name] = func
    return realDeco

#Plugin: import wh scripts
@decoOptPart("import")
def opt_include(param,env):
    return processfiles(param)

#Plugin: include files
@decoOptPart("include")
def opt_include(param,env):
    def iterfile(fli):
        for f in param:
            if not os.path.isfile(f):
                raise ExcFileError(f)
            yield open(f,"r").read()
    return "".join(iterfile(param)).strip();

#Plugin: import module
@decoOptPart("module")
def opt_maodule(param,env):
    parseMName = re.compile("^[_a-zA-Z][_a-zA-Z0-9]*(\.[_a-zA-Z][_a-zA-Z0-9]*)*$").match
    #Import module list
    def imp_modules(mlist):
        for m in mlist:
            if not parseMName(m):
                raise ExcModName(m,env["file"],env["pos"])
            try:
                mget = __import__(m,None,None,["WHTEntry"])
            except:
                raise ExcModImp(m,env["file"],env["pos"])
            if not hasattr(mget,"WHTEntry"):
                raise ExcModImp(m,env["file"],env["pos"])
            decoOptPart(m)(mget.WHTEntry)
        return ""
    return imp_modules(param)

#Plugin: variable set
@decoOptPart("set")
def opt_set(param,env):
    if len(param) != 2 or not param[0]:
        raise ExcCMDParam(env["file"],env["pos"])
    if "varb" not in env:
        env["varb"]={param[0]:param[1]}
    else:
        env["varb"][param[0]]=param[1].decode("utf-8")
    return ""

#Plugin: variable get
@decoOptPart("get")
def opt_get(param,env):
    if len(param) != 1 or not param[0]:
        raise ExcCMDParam(env["file"],env["pos"])
    if "varb" not in env or param[0] not in env["varb"]:
        raise ExcCMDVerbFound(env["file"],env["pos"],param[0])
    return env["varb"][param[0]].encode("utf-8")

#Import process
def processfiles(filelist):
    PARSETAG = re.compile("<\((\"([^\"]|[^\\\\]\\\\\")*\"(\s*,\s*(\"([^\"]|[^\\\\]\\\\\")*\"|[0-9]+(.[0-9]+)*))*)\)>").finditer
    #Scan lines position and make index {{{
    def iterLineLen(lineStr): 
        pos = 0
        for lnindex in xrange(0,len(lineStr)):
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
    def iterfile(fli):
        for f in fli:
            if not os.path.isfile(f):
                raise ExcFileError(f)
            start = 0
            fdata = open(f,"r").read()
            fdata = map(lambda instr:instr.strip(),fdata.replace("\r\n","\n").replace("\r","\n").split("\n"))
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
        for ele in iterfile(filelist):
            if type(ele) == str:
                yield(ele)
            else:
                ENV["file"] = ele[2]
                ENV["pos"] = (ele[3][0] + 1, ele[1].start() - ele[3][1] + 1)
                if ele[0][0] not in OPTLIST:
                    raise ExcCMDError(ENV["file"],ele[0][0],ENV["pos"])
                yield OPTLIST[ele[0][0]](ele[0][1:],ENV)
    return "".join(iterDoParse()).strip()

def main():
    #Entry
    args = sys.argv[1:]
    if not args or args[0] in {"-h","--help"}:
        help()
    else:
        try:
            print(processfiles(args))
        except Exception as e:
            print("error - " + e.message, file=sys.stderr)
