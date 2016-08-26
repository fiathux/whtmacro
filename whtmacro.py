#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Wonderland HTML file template
------------------------------
Fiathu Su(fiathux@gmail.com)
2015-2016
'''

import sys
import os.path
import re
import json

OPTLIST = {}
ENV = {}

# Print help text
def help():
    print("whtmacro filelist...")

class ExcFileError(Exception):
    def __init__(me,fname):
        me.message = "Invalid file name: " + fname

class ExcCMDError(Exception):
    def __init__(me,fname,cmd,pos):
        me.message = "Unknown command [%s] in file \"%s\" pos %d" % (cmd,fname,pos)

class ExcCMDParam(Exception):
    def __init__(me,fname,pos):
        me.message = "Paramete error in file \"%s\" pos %d" % (fname,pos)

class ExcCMDVerbFound(Exception):
    def __init__(me,fname,pos,vname):
        me.message = "Undefined variable name [%s] in file \"%s\" pos %d" % (vname,fname,pos)

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
    #Parse file element
    def iterfile(fli):
        for f in fli:
            if not os.path.isfile(f):
                raise ExcFileError(f)
            start = 0
            fdata = open(f,"r").read()
            pnode = PARSETAG(fdata)
            for pone in pnode:
                pickdata = fdata[start:pone.start()]
                start = pone.end()
                parse = json.loads("["+pone.group(1)+"]")
                yield pickdata
                yield (parse,pone,f)
            yield fdata[start:]
    #Parse opt-plugins
    def iterDoParse():
        for ele in iterfile(filelist):
            if type(ele) == str:
                yield(ele)
            else:
                ENV["file"] = ele[2]
                ENV["pos"] = ele[1].start()
                if ele[0][0] not in OPTLIST:
                    raise ExcCMDError(ENV["file"],ele[0][0],ENV["pos"])
                yield OPTLIST[ele[0][0]](ele[0][1:],ENV)
    #print([s for s in iterDoParse()])
    return "".join(iterDoParse()).strip()

#Entry
args = sys.argv[1:]
if not args or args[0] in {"-h","--help"}:
    help()
else:
    try:
        print(processfiles(args))
    except Exception as e:
        print("error - " + e.message);
