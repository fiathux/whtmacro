# -*- coding: utf-8 -*-

'''
Wonderland HTML file template
Text Line iterator
------------------------------
Fiathu Su(fiathux@gmail.com)
2015-2018
'''

# content line provider
class contentLine(object):
    # roll back iterate
    class CLRollBack(Exception):pass

    #
    def __init__(me, content):
        content = content.replace("\r\n","\n").replace("\r","\n")
        me._lines = content.split("\n")
        me._index = 0
        me._withstack = []

    # allow self as iterator
    def __iter__(me):
        return me

    # next item
    def __next__(me):
        if me._index >= len(me._lines):
            raise StopIteration()
        line = me._lines[me._index]
        me._index = me._index + 1
        return line

    # get current line postion
    def pos(me):
        return (me._index, len(me._lines))

    # rollback index in with statement
    def rollbreak(me):
        raise me.CLRollBack()

    # reset iterator
    def reset(me):
        me._index = 0

    # begin checkpoint
    def __enter__(me):
        me._withstack.append(me._index)
        return me

    # end checkpoint
    def __exit__(me, exc_type, exc_val, traceback):
        if exc_type is not None:
            me._index = me._withstack.pop()
            if exc_type == me.CLRollBack:
                return True
        else:
            me._withstack.pop()
