# -*- coding: utf-8 -*-

'''
Wonderland HTML file template
Order-tree module
This module implement a red-black tree. it generate without remove opreation.
build once for search quickly
------------------------------
Fiathu Su(fiathux@gmail.com)
2015-2016
'''

#Once build
class SearchTree():
    def __init__(self,comparer = lambda a,b: a>b):
        self.__comparer = comparer
        self.__root = None

    def add(self,obj):pass
