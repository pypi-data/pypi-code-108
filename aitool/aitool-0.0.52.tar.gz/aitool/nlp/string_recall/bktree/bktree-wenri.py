##bk树，支持快速召回
import Levenshtein
import pandas as pd


class BKTree:
    def __init__(self, distfn):
        """
        Create a new BK-tree from the given distance function and
        words.
        """
        self.distfn = distfn
        self.tree = ('', {})
        # it = iter(words)

    def build_bkTree(self, words):
        if words:
            self.tree = (words[0], {})
            if len(words) > 1:
                for i in words[1:]:
                    self._add_word(self.tree, i)

    def _add_word(self, parent, word):
        pword, children = parent
        try:
            d = self.distfn(word, pword)
        except:
            print(word, pword)
        if d in children:
            self._add_word(children[d], word)
        else:
            children[d] = (word, {})

    def query(self, word, n):
        """
        Return all words in the tree that are within a distance of `n'
        from `word`.
        Arguments:
        """

        def rec(parent):
            pword, children = parent
            d = self.distfn(word, pword)
            results = []
            if d <= n:
                results.append((pword, d))

            for i in range(d - n, d + n + 1):
                child = children.get(i)
                if child is not None:
                    results.extend(rec(child))
            return results

        # sort by distance
        return sorted(rec(self.tree))

    def maxdepth(self, tree, count=0):
        _, children = tree
        if len(children):
            return max(self.maxdepth(i, count + 1) for i in children.values())
        else:
            return count


def get_distance(tar_str, des_str):
    hanzi_dis = Levenshtein.distance(tar_str, des_str)
    return hanzi_dis

if __name__ == '__main__':
    approvalNbr2other = dict()
    bktree = BKTree(get_distance)
    drug_name_list = []
    for key, drugs in approvalNbr2other.items():
        for drug in drugs:
            drug_name_list.append(drug['产品名称'])
    drug_name_list = list(set(drug_name_list))
    bktree.build_bkTree(drug_name_list)  ##基于药品库建立bk-tree