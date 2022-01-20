#coding=utf-8
from aitool import exe_time
import Levenshtein
import sys
sys.setrecursionlimit(100000)

class BkTree:
    # An implementation of a BKTree. This tree allows
    # operations such as insertion, building up the
    # tree and querying the tree, or finding elements
    # of the tree which are within a specified difference
    # from a given string
    def __init__(self, list, distancefunction):
        # The initializer takes the list used in building
        # the tree and the distance function
        # The distance function in this case would
        # be the Levenshtein distance
        # The initializer also assigns the first element
        # in the list as the parent node, and adds
        # it to the discionary used for storage.
        self.df = distancefunction
        self.root = list[0]
        self.tree = (list[0], {})

    @exe_time(print_time=True)
    def builder(self, list):
        # This part of the code builds the tree by adding
        # words from the input list to the dictionary
        # storage using the class insert method
        for word in list[1:]:
            self.tree = self.insert(self.tree, word, 1)

    def insert(self, node, word, deep):
        # This method is used for inserting a word into the tree.
        # As shown in the main article, it first
        # takes the distance between the word and the parent node.
        # If the distance isn't already the weight
        # of an edge of the parent, it attaches it to the parent
        # node. Else, it recursively attempts this with
        # the children of the parent, and their children
        if deep > 2000:
            ssss = 1
        d = self.df(word, node[0])
        if d not in node[1]:
            node[1][d] = (word, {})
        else:
            self.insert(node[1][d], word, deep+1)
        return node


    def tester(self, testword, n):
        # This method performs the actual querying of the bk
        # tree to search for elements in the tree that have a
        # specified number of distance from the given string.
        # It does using another function, search function which
        # first tests for the distance between the parent of the
        # bk tree and the given string. It also appends
        # the parent string to the output list if it satisfies the
        # criteria. If not, it applies the triangle inequality,
        # checking on edges with weights that don't immediately disobey
        # the triangle inequality and adding them to the
        # Output list.
        def search(node):
            d = self.df(testword, node[0])
            output = []
            if d <= n:
                output.append(node[0])
            for i in range(d - n, d + n + 1):
                child = node[1]
                if i in child:
                    output.extend(search(node[1][i]))
            return output

        root = self.tree
        return search(root)


def make_dataset(num):
    import random
    data = []
    chs = ["1","2","3","4","5","a","b","c","d","e"]
    for i in range(num):
        lenth = random.randint(4,9)
        chr = ""
        for j in range(lenth):
            chr += chs[random.randint(0,len(chs)-1)]
        data.append(chr)
    return data


def ratio(l, chr):
    ans = []
    for lc in l:
        ans.append([lc, Levenshtein.ratio(lc, chr)])
    ans.sort(key=lambda x: x[1], reverse=True)
    return ans[:30]


@exe_time(print_time=False)
def ftree(tree, chr, n):
    l = tree.tester(chr, n)
    ans = []
    for lc in l:
        ans.append([lc, Levenshtein.ratio(lc, chr)])
    ans.sort(key=lambda x: x[1], reverse=True)
    return ans[:30]

# This part of the code is a test function , that just tests a sample case
if __name__ == '__main__':
    l = make_dataset(200000)
    # ans_candidate.append([item[3], round(1.0 * item[0], 3), item[1], item[2]])
    # ans_candidate.sort(key=lambda x: x[1], reverse=True)

    # tree = BkTree(list, Levenshteind)
    tree = BkTree(l, Levenshtein.distance)
    tree.builder(l)
    x = ftree(tree, 'a23fc', 2)
    y = ratio(l, 'a23fc')
    print("x:", len(x), x)
    print("y:", len(y), y)
