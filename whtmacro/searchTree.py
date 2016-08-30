# -*- coding: utf-8 -*-

'''
Wonderland HTML file template
Order-tree module
------------------------------
Fiathu Su(fiathux@gmail.com)
2015-2016
'''

#Basic tree node {{{
class BasicNode(object):
    def __init__(self,data):
        self.left = None
        self.right = None
        self.parent = None
        self.data = data

    def leftRotate(self):
        if self.parent and self.parent.right == self:
            if self.parent.parent:
                if self.parent.parent.left == self.parent:
                    self.parent.parent.left = self
                else:
                    self.parent.parent.right = self
            self.parent.right = self.left
            self.left = self.parent
            self.parent = self.parent.parent
            self.left.parent = self
            if self.left.right:
                self.left.right.parent = self.left
            return True
        return False

    def rightRotate(self):
        if self.parent and self.parent.left == self:
            if self.parent.parent:
                if self.parent.parent.left == self.parent:
                    self.parent.parent.left = self
                else:
                    self.parent.parent.right = self
            self.parent.left = self.right
            self.right = self.parent
            self.parent = self.parent.parent
            self.right.parent = self
            if self.right.left:
                self.right.left.parent = self.right
            return True
        return False
#}}}

#implement a red-black tree. it generate without remove opreation. build once for search quickly.
#{{{
class SearchRBTree(object):
    #Red-Black node
    class RBNode(BasicNode):
        def __init__(self,data):
            super(SearchRBTree.RBNode,self).__init__(data)
            self.red=True

    def __init__(self,comparer = lambda a,b: 1 if a>b else -1 if a<b else 0):
        self.__comparer = comparer
        self.__root = None

    def add(self,index,body):
        if not self.__root:
            self.__add_case_root(self.RBNode((index,body)))
        else:
            findnode = self.__root
            while True:
                diff = self.__comparer(findnode.data[0],index)
                if diff == 0: return False
                if diff > 0 and findnode.right:
                    findnode = findnode.right
                elif diff < 0 and findnode.left:
                    findnode = findnode.left
                else:
                    n = self.RBNode((index,body))
                    n.parent = findnode
                    if diff > 0: findnode.right = n
                    else: findnode.left = n
                    self.__add_case_parent_black(n)
                    return True

    def find(self,index):
        findnode = self.__root
        while True:
            diff = self.__comparer(findnode.data[0],index)
            if diff == 0: return findnode.data[1]
            if diff > 0 and findnode.right:
                findnode = findnode.right
            elif diff < 0 and findnode.left:
                findnode = findnode.left
            else:
                raise KeyError(index)

    #Add method{{{
    #Case 1:
    def __add_case_root(self,node):
        if not node.parent:
            self.__root = node
            node.red = False
        else:
            self.__add_case_parent_black(node)
    #Case 2:
    def __add_case_parent_black(self,node):
        if not node.parent.red: pass
        else:
            self.__add_case_parent_uncle_red(node)
    #Case 3:
    def __add_case_parent_uncle_red(self,node):
        if (node.parent.red and 
                (node.parent.parent.left and node.parent.parent.left.red) and 
                (node.parent.parent.right and node.parent.parent.right.red)):
            node.parent.parent.left.red = False
            node.parent.parent.right.red = False
            node.parent.parent.red = True
            self.__add_case_root(node.parent.parent)
        else:
            self.__add_case_parent_red_cross_direct(node)
    #Case 4:
    def __add_case_parent_red_cross_direct(self,node):
        if node.parent.right == node and node.parent.parent.left == node.parent:
            node.leftRotate()
        elif node.parent.left == node and node.parent.parent.right == node.parent:
            node.rightRotate()
        else:
            node=node.parent
        self.__add_case_parent_red_samedirect(node)
    #Case 5:
    def __add_case_parent_red_samedirect(self,node):
        node.red = False
        node.parent.red = True
        if node.parent.left == node:
            node.rightRotate()
        else:
            node.leftRotate()
        if not node.parent:
            self.__root = node
    #}}}
#}}}

