# -*- coding: utf-8 -*-
"""
Construction of the xbw transform

@author: Danilo Giovanni Dolce
@version: 0.0.1
"""

import math
import numpy as np
import copy
import os

def readAndImportTree(path):
    """
    Import a tree from an input file
    
    Parameters
    ----------
    path : string
        The absolute path of the tree to import.

    Returns
    -------
    xbwt : XBWT
        An XBWT object with the tree imported from file.
    """
    dictNodes = {}
    lastNode = None
    lastEdge = None
    blockNodes = False
    countNodes = 0
    countNodesWithEdges = 0
    blockEdges = False
    if os.path.exists(path):
        f = open(path, 'r')
        lines = f.readlines()
        cleanLines = []
        for line in lines:
            if line != '\n':
                cleanLines.append(line[:len(line)-1])
        if cleanLines[0] == "[NODES]":
            i = 0
            for line in cleanLines[1:]:
                if line == "[\\NODES]":
                     blockNodes = True
                     lastNode = i+1
                     break
                else:
                    countNodes+=1
                i+=1
            if blockNodes:
                if cleanLines[i+2] == "[EDGES]":
                    for line in cleanLines[i+3:]:
                        if line == "[\\EDGES]":
                            blockEdges = True
                            lastEdge = i+2
                            break
                        else:
                            countNodesWithEdges+=1
                        i+=1
                    if not blockEdges:
                        raise Exception("Error: The closing tag of the EDGES block was not found")
                else:
                    raise Exception("Error: The opening tag of the EDGES block was not found")
            else:
                raise Exception("Error: The closing tag of the NODES block was not found")                     
        else:
            raise Exception("Error: The opening tag of the NODES block was not found")
    else:
        raise Exception("Error: Path not exists")
    
    if countNodes > 0:
        # Reading nodes
        for i in range(1, lastNode):
            tmp = cleanLines[i].split("=")
            tmp[0] = tmp[0].strip()
            tmp[1] = tmp[1].strip()
            if len(tmp) == 2:
                if tmp[0] in dictNodes.keys():
                    raise Exception("Error: Duplicate node key")
                dictNodes[tmp[0]] = Node(str(tmp[1]))
            else:
                raise Exception("Error: Wrong input (NODE)")
    else:
        raise Exception("Error: No input nodes")
    
    if "root" not in dictNodes.keys():
        raise Exception("Error: The root node was not specified")
    
    tree = Tree()
        
    tree.insert(dictNodes["root"], None)
    
    if countNodesWithEdges > 0:
        # Reading edges
        for i in range(lastNode+2, lastEdge+1):
            tmp =  cleanLines[i].split("=")
            tmp[0] = tmp[0].strip()
            tmp[1] = tmp[1].strip()
            tmp[1] = tmp[1].replace("[", "")
            tmp[1] = tmp[1].replace("]", "")
            tmp[1] = tmp[1].replace(" ", "")
            tmp[1] =  tmp[1].split(",")
            if type(tmp[1]) == list and len(tmp[1]) > 0:
                if tmp[0] not in dictNodes.keys():
                    raise Exception("Node "+str(tmp[0])+" not exists")
                else:
                    for child in tmp[1]:
                        if child in dictNodes.keys():
                            tree.insert(dictNodes[child], dictNodes[tmp[0]])
                        else:
                            raise Exception("Node "+str(child)+" not exists")
            else:
                raise Exception("Error: Wrong input (EDGE)")
    else:
        raise Exception("Error: No input edges")
    
    xbwt = XBWT(tree)
    
    return xbwt
    
class Node(object):
    """ Node of a Tree """
    
    def __init__(self, label='root', children=None, parent=None):
        """
        Constructor

        Parameters
        ----------
        label : string, optional
            Label of the node to create. The default is 'root'.
        children : list, optional
            Children of the node to create. The default is None.
        parent : Node, optional
            Parent of the node to create. The default is None.

        Returns
        -------
        None.

        """
        self.label = label
        self.parent = parent
        self.children = []
        if children is not None:
            for child in children:
                self.add_child(child)
                
    def getLabel(self):
        """ Return the label of the node """
        return self.label
    
    def setLabel(self, label):
        """ Set a node label """
        self.label = label
    
    def getParent(self):
        """ Return the parent of the node """
        return self.parent
    
    def setParent(self, parent):
        """
        Set the parent of the node

        Parameters
        ----------
        parent : Node
            Parent node to be set.

        Returns
        -------
        None.

        """
        self.parent = parent
    
    def getChildren(self):
        """ Return the children's Array of a node"""
        return self.children
    
    def setChildren(self, children):
        """
        Set the children of the node 

        Parameters
        ----------
        children : list
            New children's list of the node.

        Returns
        -------
        None.

        """
        self.children = children
    
    def isRoot(self):
        """ Check if the node is the root """
        if self.parent is None:
            return True
        else:
            return False
        
    def isLeaf(self):
        """ Check if the node is a leaf """
        if len(self.children) == 0:
            return True
        else:
            return False
    
    def level(self):
        """ Return the level of a node """
        if self.isRoot():
            return 0
        else:
            return 1 + self.parent.level()   
    
    def isRightmost(self):
        """ 
        Return 1 if node is the rightmost children of the parent, 0
        otherwise
        """
        length_parent = len(self.parent.children)
        if length_parent!=0:
            if (self.parent.children[length_parent-1]==self):
                return 1
        return 0
    
    def addChild(self, node):
        """ Add a child at node """
        node.parent = self
        assert isinstance(node, Node)
        self.children.append(node)
        

class Tree(object):
    """ A Generic Tree """
    
    def __init__(self):
       """ Constructor """
       self.root=None
       self.height=0
       self.nodes=[]
       self.edges=[]

    def insert(self, node, parent):   
        """
        Insert a node into tree

        Parameters
        ----------
        node : Node
            Node to insert.
        parent : Node
            Parent of the node to insert.

        Returns
        -------
        None.

        """
        
        if parent is not None:
            parent.addChild(node)
            self.edges.append((parent, node))
        else:
            if self.root is None:
                self.root=node
        self.nodes.append(node)
        
    def getRoot(self):
        """ Return the root of tree"""
        return self.root
    
    def setRoot(self, root):
        """
        Set the root of the tree

        Parameters
        ----------
        root : Node
            Root of the tree to be set.

        Returns
        -------
        None.

        """
        self.root = root
    
    def getNodes(self):
        """ Return the nodes of tree"""
        return self.nodes
    
    def getEdges(self):
        """ Return the edges of tree"""
        return self.edges
    
    def setEdges(self, edges):
        """
        Set the edges of the tree

        Parameters
        ----------
        edges : list
            List of pairs of nodes representing the new edges of the tree.

        Returns
        -------
        None.

        """
        self.edges = edges
               
    def printAllNodes(self):
        """ Outputs all tree node labels """
        print("Nodes: ")
        for n in self.nodes:
            print(n.getLabel())
    
    def preorder(self, root):
        """
        Visit the tree in pre-order and return the respective list of nodes

        Parameters
        ----------
        root : Node
            The root of the tree.

        Returns
        -------
        list
            The list of tree nodes visited in pre-order.

        """
        if not root:
            return []
        result = []
        if root.children:
            for node in root.children:
                result.extend(self.preorder(node))
        return [root] + result
    
class XBWT(object):
    """ Class for the construction and management of the xbw transform """
    
    def __init__(self, T):
        """
        Contructor

        Parameters
        ----------
        T : Tree
            An ordered tree of arbitrary fan-out, depth and shape.

        Returns
        -------
        None.

        """
        self.T = T
        
    def getTree(self):
        """ Returns the tree to be used for constructing the transform """
        return self.T
    
    def setTree(self, T):
        """
        Set the tree to use for the construction of the transform

        Parameters
        ----------
        T : Tree
            Tree to use for the construction of the transform.

        Returns
        -------
        None.

        """
        self.T = T
    
    def computeIntNodesArray(self, root):
        """
        Compute the IntNodes Array needed by the PathSort algorithm

        Parameters
        ----------
        root : Node
            The root of the tree.

        Returns
        -------
        IntNodes : list
            Array of triples, where the first element represents the node 
            label, the second the level, and the third the position of the 
            node's parent in this Array. The order of the nodes is established 
            by the pre-order visit of the T tree..
        """
        
        # Array of triples (node label, level, parent position in node IntNodes)
        IntNodes = [] 
        # Keep track of the current level of a node
        level = 0 
        # Current index of the IntNodes Array
        index = 0 
        # Stores the current path (root-node) of a node
        currentPath = ""
        # Queue to analyze the various nodes in pre-order        
        Stack = [] 
        
        # Initialization  
        
        #It keeps track of the nodes visited in pre-order
        Preorder =[]  
        Preorder.append(root)
        Stack.append(root)
        
        IntNodes.append([root.getLabel(), level, 0])
        currentPath+=root.getLabel()
        index+=1
        
        posParent = {}
        posParent[root] = 1
                
        while len(Stack)>0:
            # Flag to check if all nodes have been visited
            flag = 0
            # Case 1: if the initial element of the pile is a leaf I remove
            # this item from the Stack
            if len((Stack[len(Stack)-1]).children)== 0:
                Stack.pop()
                level-=1
                # Case 2: If the starting element of the stack is a node with
                # children
            else:
                Par = Stack[len(Stack)-1]
            # When an unvisited child node is found (in sequence from left to right), 
            # place it in the stack and in the Preorder vector (visited nodes). 
            # Then, start over from case 1 to explore the visited node.
            for i in Par.getChildren():
                if i not in Preorder:
                    flag = 1
                    level+=1
                    IntNodes.append([i.getLabel(), level, posParent[i.getParent()]])
                    index+=1
                    if i.getLabel() != '$':
                        posParent[i] = index
                    Stack.append(i)
                    Preorder.append(i)
                    break
                    # If all left-to-right child nodes of a parent have been 
                    # visited, remove the parent from the stack
            if flag == 0:
                Stack.pop() 
                level-=1
       
        return IntNodes
    
    def radixSortInteger(self, Array, radix=10):
        """
        Radix-sort sorting algorithm for integer Arrays
        """
        if len(Array) == 0:
           return Array
    
        # Determine minimum and maximum values
        minValue = Array[0][1]
        maxValue = Array[0][1]
        for i in range(1, len(Array)):
           if Array[i][1] < minValue:
               minValue = Array[i][1]
           elif Array[i][1] > maxValue:
               maxValue = Array[i][1]
               
        # Perform counting sort on each exponent/digit, starting at the least
        # significant digit
        exponent = 1
        while (maxValue - minValue) / exponent >= 1:
            Array = self.countingSortByDigit(Array, radix, exponent, minValue)
            exponent *= radix
    
        return Array
    
    def countingSortByDigit(self, Array, radix, exponent, minValue):
        """
        Counting sort sorting algorithm 
        """
        bucketIndex = -1
        buckets = [0] * radix
        output = [None] * len(Array)
    
        # Count frequencies
        for i in range(0, len(Array)):
          bucketIndex = math.floor(((Array[i][1] - minValue) / exponent) % radix)
          buckets[bucketIndex] += 1
    
        # Compute cumulates
        for i in range(1, radix):
          buckets[i] += buckets[i - 1]
      
        # Move records
        for i in range(len(Array) - 1, -1, -1):
          bucketIndex = math.floor(((Array[i][1] - minValue) / exponent) % radix)
          buckets[bucketIndex] -= 1
          output[buckets[bucketIndex]] = Array[i]
          #print("Output: ", output)
        return output
    
    def radixSortLSD(self, Array, w):
        """
        Radix sort sorting algorithm for fixed length strings.
        Allows you to sort the triplets of the first iteration.

        Parameters
        ----------
        Array : list
            Array of tuples of two elements, the first represents the 
            position of the triplet in the IntNodes array, the second the 
            triplet.
        w : int
            fixed length of strings.

        Returns
        -------
        a : list
            The array of ordered triplets.
        """
        a = Array.copy()
        n = len(a)
        R = 256 # Extend ASCII alphabet size
        aux = ["" for i in range(0, n)]
        
        for d in range(w-1, -1, -1):
            # Sort by key-indexed counting on dth character
            
            count = np.zeros(R+1)
            # Count frequencies
            for i in range(0, n):
                count[ord(a[i][1][d])+1]+=1
            
            # Compute cumulates
            for r in range(0, R):
                count[r+1]+=count[r]
                 
            # Move data
            for i in range(0, n):
                #print("Count index: ", count[int(a[i][1][d])])
                aux[int(count[ord(a[i][1][d])])] = a[i]
                count[ord(a[i][1][d])]+=1
                
            # Copy back
            for i in range(0, n):
                a[i] = aux[i]
        return a
    
    def namingTriplets(self, SortedTriplets):
        """
        Name each triplet

        Parameters
        ----------
        SortedTriplets : list
            Triplets ordered.

        Returns
        -------
        lexName : list
            Array of tuples, where the first value represents the assigned 
            name, while the second value represents the position of the node 
            in IntNodes that generates the triplet.
        notUnique : bool
            False if all assigned names are different, true otherwise.
        """
        notUnique = False
        LexName = []
        LexName.append([2, SortedTriplets[0][0]])
        for i in range(1, len(SortedTriplets)):
            if SortedTriplets[i-1][1]==SortedTriplets[i][1]:
                notUnique = True
                LexName.append([LexName[i-1][0], SortedTriplets[i][0]])
            else:
                LexName.append([LexName[i-1][0]+1, SortedTriplets[i][0]])
        return LexName, notUnique
    
    def contractTree(self, IntNodes, j, LexName, firstIteration):
        """
        Create the contracted tree for the recursive step of the 
        pathSort algorithm 


        Parameters
        ----------
        IntNodes : list
            Array IntNodes.
        j : int
            This value (0, 1 o 2) is given by the level whose number of nodes 
            (mod 3) is at least equal to the total number of nodes in the 
            tree divided by 3.
        lexName : list
            Array of tuples, where the first value represents the assigned 
            name, while the second value represents the position of the node 
            in IntNodes that generates the triplet.
        firstIteration : bool
            False if the current iteration of the PathSort algorithm is 
            different from the first, True otherwise.

        Returns
        -------
        tree : Tree
            The contracted tree for the recursive step of the PathSort 
            algorithm.
        """        
             
        IntNodesTemp = []
        for i in range(len(IntNodes)):
            IntNodesTemp.append(IntNodes[i])
        if firstIteration:
            for i in range(len(lexName)):
                IntNodesTemp[lexName[i][1]][0] = str(lexName[i][0])
        if j == 0:
            IntNodesTemp[0][0] = '1'
        for i in range(len(IntNodes)):
            IntNodesTemp[i][0] = Node(IntNodesTemp[i][0])
        
        dictNext = {}
        dictNext[0]=1
        dictNext[1]=2
        dictNext[2]=0
        Edges = []
        # Reconstruction of the various edges starting from the last element of IntNodes
        if j == 0:
            for i in range(len(IntNodesTemp)-1, -1, -1):
                if IntNodesTemp[i][1]%3!=j:
                    if IntNodesTemp[i][1]%3 == dictNext[j]:
                        # If the parent is the root
                        if IntNodesTemp[i][2]==1:
                            Edges.append([IntNodesTemp[IntNodesTemp[i][2]-1][0], IntNodesTemp[i][0]])
                        else:
                            aux = IntNodesTemp[IntNodesTemp[IntNodesTemp[i][2]-1][2]-1][0]
                            Edges.append([aux, IntNodesTemp[i][0]])
                    else:
                        Edges.append([IntNodesTemp[IntNodesTemp[i][2]-1][0], IntNodesTemp[i][0]])
        else:
             for i in range(len(IntNodesTemp)-1, 0, -1):
                if IntNodesTemp[i][1]%3!=j:
                    if IntNodesTemp[i][1]%3 == dictNext[j]:
                        aux = IntNodesTemp[IntNodesTemp[IntNodesTemp[i][2]-1][2]-1][0]
                        Edges.append([aux, IntNodesTemp[i][0]])
                    else:
                        Edges.append([IntNodesTemp[IntNodesTemp[i][2]-1][0], IntNodesTemp[i][0]])
        
        tree=Tree()
        tree.insert(IntNodesTemp[0][0], None)
        for i in range(len(Edges)-1, -1, -1):
            tree.insert(Edges[i][1], Edges[i][0])
        
        return tree
        
            
    def merge(self, sV, PosFirstSort, PosSecondSort, IntNodes, jV, dummyRoot = False, firstIteration = False):
        """
        Merge the PosFirst and PosSecond ordered position arrays

        Parameters
        ----------
        sV : int
            Number of dummy triples adds to IntNodesTemp.
        PosFirstSort : list
            Array of PosFirst ordered positions.
        PosSecondSort : list
            Array of PosSecond ordered positions.
        IntNodes : list
            Array IntNodes.
        jV : TYPE
            This value (0, 1 o 2) is given by the level whose number of nodes 
            (mod 3) is at least equal to the total number of nodes in the 
            tree divided by 3.
        dummyRoot : bool, optional
            True if the contracted tree has a dummy root due to the removal 
            of nodes at level 0 (mod 3). The default is False.
        firstIteration : bool, optional
            False if the current iteration of the PathSort algorithm is 
            different from the first, True otherwise. The default is False.

        Returns
        -------
        list
        Merge the PosFirst and PosSecond ordered position arrays.

        """
        
        dictCond = {}
        dictCond[0] = 1
        dictCond[1] = 2
        dictCond[2] = 0
        
        IN = IntNodes.copy()
        
        Merge = []
        i = 0 # index PosFirstSort
        j = 0 # index PosSecondSort
        
       
        flag = True
        while flag:
            if IntNodes[PosFirstSort[i]+sV][1]%3 == dictCond[jV]:
                pair1 = [IN[IN[PosFirstSort[i]+sV][2]][0], IN[IN[IN[PosFirstSort[i]+sV][2]][2]][0]]
                pair2 = [IN[IN[PosSecondSort[j]+sV][2]][0], IN[IN[IN[PosSecondSort[j]+sV][2]][2]][0]]
                if not firstIteration:
                    pair1 = [int(IN[PosFirstSort[i]+sV][0])]
                    pair2 = [int(IN[PosSecondSort[j]+sV][0])]
                if pair2[0] == pair1[0]:
                    if pair2[1] == pair1[1]:
                        if PosFirstSort.index(IN[IN[IN[PosSecondSort[j]+sV][2]][2]][2]-sV) > PosFirstSort.index(IN[IN[IN[PosFirstSort[i]+sV][2]][2]][2]-sV):
                            Merge.append(PosFirstSort[i])
                            i+=1
                        else:
                            Merge.append(PosSecondSort[j])
                            j+=1
                    elif pair2[1] > pair1[1]:
                        Merge.append(PosFirstSort[i])
                        i+=1
                    else:
                        Merge.append(PosSecondSort[j])
                        j+=1
                elif pair2[0] > pair1[0]:
                      Merge.append(PosFirstSort[i])
                      i+=1
                else:
                    Merge.append(PosSecondSort[j])
                    j+=1
                    
            elif IntNodes[PosFirstSort[i]+sV][1]%3 == dictCond[dictCond[jV]]:
                val1 = IN[IN[PosFirstSort[i]+sV][2]][0]
                val2 = IN[IN[PosSecondSort[j]+sV][2]][0]
                if not firstIteration:
                    val1 = int(IN[PosFirstSort[i]+sV][0])
                    val2 = int(IN[PosSecondSort[j]+sV][0])
                if val2 == val1:
                    if PosFirstSort.index(IN[PosSecondSort[j]+sV][2]-sV) > PosFirstSort.index(IN[PosFirstSort[i]+sV][2]-sV):
                        Merge.append(PosFirstSort[i])
                        i+=1
                    else:
                        Merge.append(PosSecondSort[j])
                        j+=1
                elif val2 > val1:
                    Merge.append(PosFirstSort[i])
                    i+=1
                else:
                    Merge.append(PosSecondSort[j])
                    j+=1
                    
            if j >= len(PosSecondSort):
                for index in range(i, len(PosFirstSort)):
                    Merge.append(PosFirstSort[index])
                flag = False
            
            if i >= len(PosFirstSort):
                for index in range(j, len(PosSecondSort)):
                    Merge.append(PosSecondSort[index])
                flag = False
        
        if dummyRoot:
            pos=1
            if firstIteration:
                pos = 0
            return [Merge[i] for i in range(pos, len(Merge))]
        else:
            return Merge
       
    
    def pathSort(self, T, dummyRoot = False, firstIteration = True, rem=0, maxName=0):
        """
        Calculate the array of the positions of the ordered nodes of a generic 
        T-tree based on their upward paths.

        Parameters
        ----------
        T : Tree
            An ordered tree of arbitrary fan-out, depth and shape.
        dummyRoot : bool, optional
            True if the contracted tree has a dummy root due to the removal 
            of nodes at level 0 (mod 3). The default is False.
        firstIteration : bool, optional
            False if the current iteration of the PathSort algorithm is 
            different from the first, True otherwise. The default is True.
        rem : int, optional
            Number of nodes to be removed in the calculation of level 0 nodes 
            (mod 3) by dummy root. The default is 0.
        maxName : int, optional
            The highest name assigned when naming the triplets. 
            The default is 0.

        Returns
        -------
        IntNodes : list
            The array IntNodes.
        
        list
            The array of IntNodes ordered positions.
        """
                
        IntNodes = self.computeIntNodesArray(T.getRoot())
                                
        # Number of nodes at level j = 0, 1, 2 mod 3
        NNL = np.zeros(3, dtype="int")
        for i in IntNodes:
            NNL[i[1]%3]+=1
        NNL[0]-=rem
        
        # t/3
        if rem > 0:
            x = math.ceil((len(IntNodes)-rem)/3)
        else:
            x = math.ceil(len(IntNodes)/3)
        
        # Compute j value
        j = None
        for i in range(len(NNL)):
            if NNL[i]>=x:
                j=i
                break
        
        PosFirst = []
        PosSecond = []
        for i in range(len(IntNodes)):
            if IntNodes[i][1] % 3 != j:
                PosFirst.append(i)
            else:
                PosSecond.append(i)
        
        # Inserting dummy triples in a temporary IntNodes Array
        IntNodesTemp = []
        inc=0
        if j!=0:
            inc=3
            IntNodesTemp.append(['0', -3, -1])
            IntNodesTemp.append(['0', -2, 0])
            IntNodesTemp.append(['0', -1, 1])
            for i in range(len(IntNodes)):
                temp = list(IntNodes[i])
                temp[2]+=2
                IntNodesTemp.append(temp)
        else:
            inc=2
            IntNodesTemp.append(['0', -2, -1])
            IntNodesTemp.append(['0', -1, 0])
            for i in range(len(IntNodes)):
                temp = list(IntNodes[i])
                temp[2]+=1
                IntNodesTemp.append(temp)
        
        Triplets = []
        for i in PosFirst:
            TripletContainer = []
            Triple = []
            index=i+inc
            TripletContainer.append(i)
            for c in range(3):
                Triple.append(IntNodesTemp[IntNodesTemp[index][2]][0])
                index = IntNodesTemp[index][2]
            TripletContainer.append(Triple)
            Triplets.append(TripletContainer)
        
        if firstIteration:
            SortedTriplets = self.radixSortLSD(Triplets, 3)
        else:
            SortedTriplets = self.radixSortInteger([[e[0], int(''.join(e[1]))] for e in Triplets])
        
        LexName, notUnique = self.namingTriplets(SortedTriplets)
                
        maxName = LexName[len(LexName)-1][0]
        
        APosFirstSort = np.zeros(len(Triplets), dtype="int")
        if notUnique:
            cTree = self.contractTree(copy.deepcopy(IntNodes), j, LexName, firstIteration)
            rem+=1
            if j!=0:
                APosFirstSort = self.pathSort(cTree, False, False, rem, maxName) # prima era true
            else: 
                APosFirstSort = self.pathSort(cTree, True, False, rem, maxName)
        else:
            for i in range(len(SortedTriplets)):
                APosFirstSort[i] = PosFirst.index(SortedTriplets[i][0]) # rivedere visto la modifica precedente
                
        if j==0:
            for i in range(len(APosFirstSort)):
                APosFirstSort[i]-=1
        
        # Compute PosFirstSort
        PosFirstSort = []
        for i in range(len(APosFirstSort)):
            PosFirstSort.append(PosFirst[APosFirstSort[i]])        
        
        # Compute PosSecondSort
        PosSecondSort = np.zeros(len(PosSecond), dtype="int")
        Pairs = []
        c = 0
        
        if not firstIteration:
            if j == 0:
                Pairs.append((IntNodesTemp[PosSecond[0]+inc][0], 0, PosSecond[0]))
                c = 1
            for i in range(c, len(PosSecond)):
                Pairs.append((IntNodesTemp[PosSecond[i]+inc][0], 
                             PosFirstSort.index(IntNodesTemp[PosSecond[i]+inc][2]-inc), PosSecond[i]))
        else:
            if j==0:
                Pairs.append((IntNodesTemp[IntNodesTemp[PosSecond[0]+inc][2]][0], 
                          0, PosSecond[0]))
                c = 1
            for i in range(c, len(PosSecond)):
                Pairs.append((IntNodesTemp[IntNodesTemp[PosSecond[i]+inc][2]][0], 
                         PosFirstSort.index(IntNodesTemp[PosSecond[i]+inc][2]-inc), PosSecond[i]))
        
        SortedPairs = copy.deepcopy(Pairs)
        # I sort by the first element, otherwise by the second
        if firstIteration:
            SortedPairs.sort(key=lambda x:(x[0], int(x[1])))
        else:
            SortedPairs.sort(key=lambda x:(int(x[0]), int(x[1])))

        for i in range(len(SortedPairs)):
            PosSecondSort[i] = SortedPairs[i][2]
        
        if not firstIteration:
            return self.merge(inc, PosFirstSort, PosSecondSort, IntNodesTemp, j, dummyRoot, firstIteration)
        else:
            return IntNodes, self.merge(inc, PosFirstSort, PosSecondSort, IntNodesTemp, j, dummyRoot, firstIteration)
    
    def computeSpiSort(self, IntNodes, IntNodesPosSort):
        """
        Calculate the ordered Spi component

        Parameters
        ----------
        IntNodes : list
            The array IntNodes.
        IntNodesPosSort : list
            The array of IntNodes ordered positions.

        Returns
        -------
        Spi : list
            The ordered Spi component.

        """
        Spi = []
        Spi.append('') # root
        labelRoot = IntNodes[0][0]
        for i in range(1, len(IntNodes)):
            spi = ""
            j = IntNodesPosSort[i]
            while IntNodes[IntNodes[j][2]-1][0] != labelRoot:
                spi+=IntNodes[IntNodes[j][2]-1][0]
                j = IntNodes[j][2]-1
            spi+=labelRoot
            Spi.append(spi)
        return Spi
    
    def printXBWT(self, S):
        """
        Print the xbwt transform on the screen

        Parameters
        ----------
        S : list
            The xbwt transform of the tree T.

        Returns
        -------
        None.

        """
        print("*** XBW TRANSFORM OF THE TREE T *** \n")
        print("[S_LAST, S_ALPHA]\n")
        for item in S:
            print(item)

    def computeXBWT(self):
        if self.getTree():
            IntNodes, IntNodesPosSort = self.pathSort(self.getTree())
        else:
            raise Exception("No input tree")
        """
        Compute the xbw transform

        Returns
        -------
        S : list
            The xbw transform of the tree T.

        """
        # SLast
        PosLast = np.zeros(len(IntNodes), dtype="int")
        for i in range(1, len(IntNodes)):
            PosLast[IntNodes[i][2]-1]= i
        PosLast = list(set(PosLast))[1:]
        SLast = np.zeros(len(IntNodes), dtype='int')
        for i in PosLast:
            SLast[i]=1
            
        # SAlpha (bit)
        NodeFlag = np.ones(len(IntNodes), dtype="int")
        for i in range(1, len(IntNodes)):
            NodeFlag[IntNodes[i][2]-1]= 0
        
        S = []
        for i in range(len(IntNodes)):
            S.append(list((SLast[IntNodesPosSort[i]], [IntNodes[IntNodesPosSort[i]][0], NodeFlag[IntNodesPosSort[i]]])))
        return S